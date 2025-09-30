# app/db.py
from pymongo import MongoClient

# Use the default port from our docker-compose file
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client['asr_database'] # Database name
transcriptions_collection = db['transcriptions'] # Collection name