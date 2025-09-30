# workers/celery_config.py
from celery import Celery

# The broker URL points to our RabbitMQ container
BROKER_URL = 'amqp://user:password@localhost:5672/'

# NEW: The backend URL points to our MongoDB container to store results
RESULT_BACKEND = 'mongodb://localhost:27017/celery_results' # Using a new DB 'celery_results'

celery_app = Celery(
    'tasks',
    broker=BROKER_URL,
    backend=RESULT_BACKEND, # <--- ADD THIS LINE
    include=['workers.tasks']
)