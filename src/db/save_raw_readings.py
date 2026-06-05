from datetime import datetime, timezone

from src.api.airthings_client import get_access_token, get_latest_samples
from src.db.mongo_client import get_database


DEVICE_ID = "2960154462"

db = get_database()
collection = db["raw_readings"]

token = get_access_token()
samples_response = get_latest_samples(token, DEVICE_ID)

document = {
    "source": "airthings",
    "device_id": DEVICE_ID,
    "pulled_at": datetime.now(timezone.utc),
    "raw": samples_response,
}

result = collection.insert_one(document)

print("Inserted raw readings document ID:", result.inserted_id)
print(samples_response)