from datetime import datetime, timezone
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from src.db.mongo_client import get_database


load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))

db = client["airthings_dashboard"]
collection = db["raw_readings"]

test_doc = {
    "source": "airthings",
    "device_id": "test_device",
    "recorded_at": datetime.now(timezone.utc),
    "metrics": {
        "temp_f": 72.5,
        "humidity": 50
    }
}

result = collection.insert_one(test_doc)

print("Inserted ID:", result.inserted_id)
print(client.list_database_names())


db = get_database()
collection = db["raw_readings"]