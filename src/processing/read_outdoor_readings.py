import pandas as pd

from src.db.mongo_client import get_database


def get_outdoor_readings_df(limit=100):
    db = get_database()
    collection = db["outdoor_readings"]

    cursor = collection.find().sort("recorded_at", -1).limit(limit)
    readings = list(cursor)

    if not readings:
        return pd.DataFrame()

    df = pd.DataFrame(readings)

    if "recorded_at" in df.columns:
        df["recorded_at"] = pd.to_datetime(df["recorded_at"], utc=True)
        df["recorded_at_local"] = df["recorded_at"].dt.tz_convert("America/Los_Angeles")

    if "pulled_at" in df.columns:
        df["pulled_at"] = pd.to_datetime(df["pulled_at"], utc=True)
        df["pulled_at_local"] = df["pulled_at"].dt.tz_convert("America/Los_Angeles")

    return df