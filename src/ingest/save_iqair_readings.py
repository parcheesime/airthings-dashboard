from datetime import datetime, timezone

from src.api.iqair_client import get_outdoor_reading
from src.db.mongo_client import get_database


def save_iqair_reading():
    reading = get_outdoor_reading()

    reading["recorded_at"] = datetime.fromisoformat(
        reading["recorded_at"].replace("Z", "+00:00")
    )
    reading["ingested_at"] = datetime.now(timezone.utc)

    db = get_database()
    result = db["outdoor_readings"].insert_one(reading)

    print(f"Saved IQAir reading: {result.inserted_id}")
    print(
        reading["location_name"],
        reading["recorded_at"],
        reading["aqi_us"],
    )


if __name__ == "__main__":
    save_iqair_reading()