from datetime import datetime, timezone

from src.api.airthings_client import get_access_token, get_latest_samples
from src.db.mongo_client import get_database


DEVICE_ID = "2960154462"

db = get_database()
collection = db["raw_readings"]

token = get_access_token()
samples_response = get_latest_samples(token, DEVICE_ID)

data = samples_response["data"]

recorded_at_unix = data.get("time")
recorded_at = datetime.fromtimestamp(recorded_at_unix, tz=timezone.utc)

document = {
    "source": "airthings",
    "device_id": DEVICE_ID,
    "recorded_at": recorded_at,
    "recorded_at_unix": recorded_at_unix,
    "pulled_at": datetime.now(timezone.utc),

    "battery": data.get("battery"),
    "co2": data.get("co2"),
    "humidity": data.get("humidity"),
    "pm1": data.get("pm1"),
    "pm25": data.get("pm25"),
    "pressure": data.get("pressure"),
    "radon_short_term_avg": data.get("radonShortTermAvg"),
    "temp": data.get("temp"),
    "voc": data.get("voc"),

    "relay_device_type": data.get("relayDeviceType"),
    "rssi": data.get("rssi"),

    "raw": samples_response,
}

result = collection.insert_one(document)

print("Inserted raw readings document ID:", result.inserted_id)
print(document)