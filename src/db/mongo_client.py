# src/db/mongo_client.py

import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def get_database():
    client = MongoClient(os.getenv("MONGODB_URI"))
    return client["airthings_dashboard"]