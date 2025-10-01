# IndieSR

A scalable, production-ready speech recognition system for Indian languages powered by NVIDIA NeMo-based IndicConformer models.

## Features

- **Multi-language Support**: Transcribe audio in Bengali, Hindi, English, and more Indian languages
- **Asynchronous Processing**: Background task processing with Celery for handling long transcriptions
- **Scalable Architecture**: Microservices design with Docker support
- **Real-time Updates**: Poll-based status tracking for transcription progress
- **Persistent Storage**: MongoDB integration for storing transcription history
- **Clean Web UI**: Simple and intuitive interface for audio upload and transcription

## Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   FastAPI   │─────▶│  RabbitMQ   │─────▶│   Celery    │
│  (Web App)  │      │  (Broker)   │      │  (Workers)  │
└─────────────┘      └─────────────┘      └─────────────┘
       │                                          │
       │                                          │
       ▼                                          ▼
┌─────────────┐                          ┌─────────────┐
│   MongoDB   │◀─────────────────────────│  NeMo ASR   │
│  (Storage)  │                          │   Models    │
└─────────────┘                          └─────────────┘
```

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- FFmpeg (for audio preprocessing)
- CUDA-capable GPU (optional, but recommended for faster inference)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/saomyaraj/IndieSR.git
cd IndieSR
```

### 2. Start Infrastructure Services

```bash
docker-compose up -d
```

This will start:

- **RabbitMQ** on ports 5672 (AMQP) and 15672 (Management UI)
- **MongoDB** on port 27017

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the FastAPI Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Start Celery Workers

In a separate terminal:

```bash
celery -A workers.celery_config worker --loglevel=info
```

### 6. Access the Application

Open your browser and navigate to:

```
http://localhost:8000
```

## Usage

1. **Select Language**: Choose the source language of your audio file
2. **Upload Audio**: Select an audio file (supported formats: WAV, MP3, FLAC, etc.)
3. **Transcribe**: Click the "Transcribe" button
4. **Wait**: The system will process your audio in the background
5. **View Result**: Transcription will appear once processing is complete

*Additional languages can be configured in `workers/tasks.py`*

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# MongoDB
MONGO_URI=mongodb://localhost:27017/

# RabbitMQ
CELERY_BROKER_URL=amqp://user:password@localhost:5672//
CELERY_RESULT_BACKEND=rpc://

# Model Settings
DEVICE=cuda  # or 'cpu' if no GPU available
```

### Adding More Languages

Edit the `model_map` in `workers/tasks.py`:

```python
model_map = {
    'bn': 'ai4bharat/indicconformer_stt_bn_hybrid_ctc_rnnt_large',
    'hi': 'ai4bharat/indicconformer_stt_hi_hybrid_ctc_rnnt_large',
    'en': 'ai4bharat/indicconformer_stt_en_conformer_ctc_large',
    # Add more languages here
}
```

## Docker Deployment (Optional)

For a fully containerized deployment:

```bash
# Build and run all services
docker-compose -f docker-compose.full.yml up --build
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
