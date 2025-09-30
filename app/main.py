# app/main.py
import os
import shutil
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# Import the celery app instance and AsyncResult to check task status
from workers.celery_config import celery_app
from celery.result import AsyncResult

from workers.tasks import transcribe_audio

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "temp_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/transcribe")
async def create_transcription_task(language: str = Form(...), audio: UploadFile = File(...)):
    """
    Accepts audio upload, saves it, and dispatches a Celery task.
    """
    if not audio:
        return JSONResponse(status_code=400, content={"message": "No audio file provided."})
    
    file_location = os.path.join(UPLOAD_DIR, audio.filename)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(audio.file, file_object)

    task = transcribe_audio.delay(file_path=file_location, language=language, original_filename=audio.filename)

    return JSONResponse(
        status_code=202, 
        content={"message": "Transcription task started!", "task_id": task.id}
    )

# --- NEW ENDPOINT ---
@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Poll this endpoint with a task_id to check the transcription status.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.ready():
        # Task is finished
        if task_result.successful():
            return {"state": task_result.state, "result": task_result.result}
        else: # Task failed
            return {
                "state": task_result.state, 
                "error": str(task_result.info) # Get the exception info
            }
    else:
        # Task is still running
        return {"state": task_result.state}