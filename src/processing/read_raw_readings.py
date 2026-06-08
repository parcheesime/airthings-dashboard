from src.db.mongo_client import get_database
import pandas as pd


def get_readings_df(limit=100):
    db = get_database()
    collection = db["raw_readings"]

    cursor = (
        collection.find(
            {
                "recorded_at": {"$exists": True}
            },
            {
                "_id": 0,
                "recorded_at": 1,
                "pulled_at": 1,
                "temp": 1,
                "humidity": 1,
                "co2": 1,
                "voc": 1,
                "pm1": 1,
                "pm25": 1,
                "radon_short_term_avg": 1,
                },
        )
        .sort("recorded_at", -1)
        .limit(limit)
        )

    df = pd.DataFrame(list(cursor))
    df["recorded_at"] = pd.to_datetime(df["recorded_at"], utc=True)
    df["pulled_at"] = pd.to_datetime(df["pulled_at"], utc=True)

    df["recorded_at_local"] = df["recorded_at"].dt.tz_convert("America/Los_Angeles")
    df["pulled_at_local"] = df["pulled_at"].dt.tz_convert("America/Los_Angeles")
    df = df.dropna(subset=["recorded_at"])
    df = df.dropna(how="all", subset=["co2", "humidity", "pm1", "pm25", "temp", "voc"])
    df["temp_f"] = (df["temp"] * 9 / 5) + 32
    df = df.sort_values("recorded_at")

    return df



if __name__ == "__main__":
    df = get_readings_df(limit=100)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nShape:")
    print(df.shape)

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nData types:")
    print(df.dtypes)

    print("\nSample rows:")
    print(
        df[
            [
                "recorded_at",
                "pulled_at",
                "temp_f",
                "humidity",
                "co2",
                "voc",
                "pm25",
                "radon_short_term_avg",
            ]
        ].head()
    )