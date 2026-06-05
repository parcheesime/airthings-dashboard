from src.db.mongo_client import get_database

db = get_database()
collection = db["raw_readings"]

latest = collection.find_one(sort=[("_id", -1)])

print(latest["raw"])