import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PURPLEAIR_API_KEY")

headers = {
    "X-API-Key": api_key
}

response = requests.get(
    "https://api.purpleair.com/v1/sensors/28701",
    headers=headers,
)

print(response.status_code)
print(response.json())