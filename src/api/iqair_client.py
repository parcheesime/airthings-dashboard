import os

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("IQAIR_API_KEY")
LATITUDE = os.getenv("IQAIR_LATITUDE")
LONGITUDE = os.getenv("IQAIR_LONGITUDE")

BASE_URL = "https://api.airvisual.com/v2/nearest_city"


def get_outdoor_reading() -> dict:
    if not API_KEY:
        raise ValueError("IQAIR_API_KEY is not set")

    if not LATITUDE or not LONGITUDE:
        raise ValueError("IQAIR_LATITUDE and IQAIR_LONGITUDE must be set")

    params = {
        "lat": LATITUDE,
        "lon": LONGITUDE,
        "key": API_KEY,
    }

    response = requests.get(BASE_URL, params=params, timeout=15)
    response.raise_for_status()

    payload = response.json()
    data = payload["data"]
    pollution = data["current"]["pollution"]
    weather = data["current"]["weather"]

    return {
        "provider": "iqair",
        "location_name": data["city"],
        "state": data["state"],
        "country": data["country"],
        "aqi_us": pollution["aqius"],
        "main_pollutant": pollution["mainus"],
        "temperature_c": weather["tp"],
        "humidity": weather["hu"],
        "wind_speed": weather["ws"],
        "recorded_at": pollution["ts"],
    }


if __name__ == "__main__":
    reading = get_outdoor_reading()
    print("SUCCESS")
    print(reading)