import requests
import time
import json

# List of MEV Relays
mev_relays = [
    "https://0xa1559ace749633b997cb3fdacffb890aeebdb0f5a3b6aaa7eeeaf1a38af0a8fe88b9e4b1f61f236d2e64d95733327a62@relay.ultrasound.money",
    "https://0x8c4ed5e24fe5c6ae21018437bde147693f68cda427cd1122cf20819c30eda7ed74f72dece09bb313f2a1855595ab677d@titanrelay.xyz",
    # Add more relays as needed
]

def get_validator_slots(relay_url):
    try:
        response = requests.get(f"{relay_url}/relay/v1/builder/validators")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying {relay_url}: {e}")
        return []
