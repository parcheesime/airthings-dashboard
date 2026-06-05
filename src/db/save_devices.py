from datetime import datetime, timezone

from src.api.airthings_client import get_access_token, get_devices
from src.db.mongo_client import get_database


db = get_database()
collection = db["devices"]

token = get_access_token()
devices_response = get_devices(token)

document = {
    "source": "airthings",
    "pulled_at": datetime.now(timezone.utc),
    "raw": devices_response,
}

result = collection.insert_one(document)

print("Inserted devices document ID:", result.inserted_id)