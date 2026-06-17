import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv

load_dotenv()

PURPLEAIR_API_KEY = os.getenv("PURPLEAIR_API_KEY")
PURPLEAIR_SENSOR_INDEX = os.getenv("PURPLEAIR_SENSOR_INDEX")

BASE_URL = "https://api.purpleair.com/v1/sensors"
LOCAL_TIMEZONE = ZoneInfo("America/Los_Angeles")


def unix_to_utc(timestamp):
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def unix_to_local(timestamp):
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone(LOCAL_TIMEZONE)


def get_sensor_data(sensor_index=None):
    """
    Get current PurpleAir sensor data and return a normalized dict.
    """

    if not PURPLEAIR_API_KEY:
        raise ValueError("Missing PURPLEAIR_API_KEY in .env")

    sensor_index = sensor_index or PURPLEAIR_SENSOR_INDEX

    if not sensor_index:
        raise ValueError("Missing PURPLEAIR_SENSOR_INDEX in .env")

    url = f"{BASE_URL}/{sensor_index}"

    headers = {
        "X-API-Key": PURPLEAIR_API_KEY
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    payload = response.json()
    sensor = payload["sensor"]
    stats = sensor.get("stats", {})

    recorded_at_unix = sensor.get("last_seen")
    data_time_stamp_unix = payload.get("data_time_stamp")
    api_time_stamp_unix = payload.get("time_stamp")

    return {
        "source": "purpleair",
        "sensor_index": sensor.get("sensor_index"),
        "station_name": sensor.get("name"),

        "recorded_at": unix_to_utc(recorded_at_unix),
        "recorded_at_local": unix_to_local(recorded_at_unix),
        "recorded_at_unix": recorded_at_unix,

        "data_time_stamp": unix_to_utc(data_time_stamp_unix),
        "data_time_stamp_local": unix_to_local(data_time_stamp_unix),
        "data_time_stamp_unix": data_time_stamp_unix,

        "api_time_stamp": unix_to_utc(api_time_stamp_unix),
        "api_time_stamp_local": unix_to_local(api_time_stamp_unix),
        "api_time_stamp_unix": api_time_stamp_unix,

        "pm1": sensor.get("pm1.0"),
        "pm25": sensor.get("pm2.5"),
        "pm25_a": sensor.get("pm2.5_a"),
        "pm25_b": sensor.get("pm2.5_b"),
        "pm25_alt": sensor.get("pm2.5_alt"),

        "pm25_10minute": stats.get("pm2.5_10minute"),
        "pm25_30minute": stats.get("pm2.5_30minute"),
        "pm25_60minute": stats.get("pm2.5_60minute"),
        "pm25_24hour": stats.get("pm2.5_24hour"),

        "pm10": sensor.get("pm10.0"),

        "temperature_f": sensor.get("temperature"),
        "humidity": sensor.get("humidity"),
        "pressure": sensor.get("pressure"),

        "confidence": sensor.get("confidence"),
        "rssi": sensor.get("rssi"),
        "latitude": sensor.get("latitude"),
        "longitude": sensor.get("longitude"),

        "raw": payload,
    }


if __name__ == "__main__":
    data = get_sensor_data()

    print("SUCCESS")
    print(f"Sensor: {data['station_name']}")
    print(f"Recorded local: {data['recorded_at_local']}")
    print(f"PM2.5 current: {data['pm25']}")
    print(f"PM2.5 10-min: {data['pm25_10minute']}")
    print(f"Temp: {data['temperature_f']} °F")
    print(f"Humidity: {data['humidity']}%")