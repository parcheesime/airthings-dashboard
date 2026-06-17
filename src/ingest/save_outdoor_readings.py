from src.api.purpleair_client import get_sensor_data
from src.db.mongo_client import get_database

db = get_database()
collection = db["outdoor_readings"]

reading = get_sensor_data()

collection.update_one(
    {
        "source": reading["source"],
        "sensor_index": reading["sensor_index"],
        "recorded_at": reading["recorded_at"],
    },
    {"$setOnInsert": reading},
    upsert=True,
)

print("Saved outdoor reading")
print(reading["station_name"], reading["recorded_at_local"], reading["pm25"])