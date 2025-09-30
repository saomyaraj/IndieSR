# workers/tasks.py
import os
import subprocess
import torch
import nemo.collections.asr as nemo_asr
from .celery_config import celery_app
from app.db import transcriptions_collection
from datetime import datetime

# --- ASR Model Loading ---
# Insight: Loading models is slow. Let's cache them in memory
# so they are loaded only once per worker process.
MODELS_CACHE = {}
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_model(language_code: str):
    if language_code in MODELS_CACHE:
        return MODELS_CACHE[language_code]
    
    # Map your dropdown language codes to the model names
    model_map = {
        'bn': 'ai4bharat/indicconformer_stt_bn_hybrid_ctc_rnnt_large',
        'hi': 'ai4bharat/indicconformer_stt_as_hybrid_ctc_rnnt_large',
        'en': 'ai4bharat/indicconformer_stt_gu_conformer_ctc_large'
        # ... add the other 8 models you want here ...
    }
    
    model_name = model_map.get(language_code)
    if not model_name:
        raise ValueError(f"Unsupported language code: {language_code}")

    print(f"Loading model for '{language_code}'...")
    model = nemo_asr.models.ASRModel.from_pretrained(model_name)
    model.freeze()
    model.to(DEVICE)
    MODELS_CACHE[language_code] = model
    print("Model loaded.")
    return model

@celery_app.task
def transcribe_audio(file_path: str, language: str, original_filename: str):
    """
    Celery task to transcribe an audio file.
    """
    try:
        # 1. Pre-process audio with FFmpeg
        base_path, _ = os.path.splitext(file_path)
        processed_path = f"{base_path}_16k_mono.wav"
        
        # This command converts the audio as required by the model
        command = ['ffmpeg', '-y', '-i', file_path, '-ac', '1', '-ar', '16000', processed_path]
        subprocess.run(command, check=True, capture_output=True)

        # 2. Get the correct ASR model
        model = get_model(language)

        # 3. Transcribe
        # Note: IndicConformer can use 'ctc' or 'rnnt'. Let's use ctc for simplicity.
        model.cur_decoder = "ctc"
        transcription = model.transcribe([processed_path], batch_size=1, language_id=language)[0]
        
        print(f"Transcription for {original_filename}: {transcription}")

        # 4. Save to MongoDB
        result = {
            'filename': original_filename,
            'language': language,
            'transcription': transcription,
            'timestamp': datetime.utcnow()
        }
        transcriptions_collection.insert_one(result)

        # 5. Clean up the audio files
        os.remove(file_path)
        os.remove(processed_path)
        
        return {"status": "success", "transcription": transcription}

    except Exception as e:
        # If something fails, clean up and log the error
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(processed_path):
            os.remove(processed_path)
        print(f"Error processing {original_filename}: {e}")
        return {"status": "error", "message": str(e)}