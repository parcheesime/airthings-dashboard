import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

CLIENT_ID = os.getenv("AIRTHINGS_CLIENT_ID")
CLIENT_SECRET = os.getenv("AIRTHINGS_CLIENT_SECRET")

TOKEN_URL = "https://accounts-api.airthings.com/v1/token"

DEVICES_URL = "https://ext-api.airthings.com/v1/devices"


def get_access_token():
    """
    Request OAuth access token from Airthings
    """

    payload = {
        "grant_type": "client_credentials",
        "scope": "read:device:current_values"
    }

    response = requests.post(
        TOKEN_URL,
        data=payload,
        auth=(CLIENT_ID, CLIENT_SECRET)
    )

    # Raise error if request failed
    response.raise_for_status()

    token_data = response.json()

    return token_data["access_token"]


def get_devices(access_token):
    """
    Retrieve devices connected to account
    """

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(
        DEVICES_URL,
        headers=headers
    )

    response.raise_for_status()

    return response.json()


if __name__ == "__main__":

    print("Getting access token...")

    token = get_access_token()

    print("SUCCESS")
    print(f"Token starts with: {token[:20]}...")
    print()

    print("Requesting devices...")

    devices = get_devices(token)

    print("DEVICES:")
    print(devices)