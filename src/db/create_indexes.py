from src.db.mongo_client import get_database

db = get_database()

raw_readings = db["raw_readings"]

raw_readings.create_index("recorded_at")
raw_readings.create_index([("device_id", 1), ("recorded_at", -1)])

print("Indexes created for raw_readings")