import requests
import time
import json

MEV_RELAYS = [
    "https://0xa1559ace749633b997cb3fdacffb890aeebdb0f5a3b6aaa7eeeaf1a38af0a8fe88b9e4b1f61f236d2e64d95733327a62@relay.ultrasound.money",
    "https://0x8c4ed5e24fe5c6ae21018437bde147693f68cda427cd1122cf20819c30eda7ed74f72dece09bb313f2a1855595ab677d@titanrelay.xyz",
]

EPOCH_DURATION = 12 * 32  # Approximate duration of an epoch in seconds

def fetch_relay_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

def extract_slots(data):
    return [entry["slot"] for entry in data]

def get_most_complete_slot_list(slot_lists):
    max_length = 0
    most_complete_list = []

    for slots in slot_lists:
        if len(slots) > max_length:
            max_length = len(slots)
            most_complete_list = slots

    return most_complete_list

def cross_check_slots(most_complete_list, slot_lists):
    missing_slots = {}

    for i, slots in enumerate(slot_lists):
        missing = set(most_complete_list) - set(slots)
        missing_slots[f"relay_{i}"] = list(missing)

    return missing_slots

def main():
    while True:
        slot_lists = []

        # Fetch data from all relays
        for relay in MEV_RELAYS:
            data = fetch_relay_data(relay)
            if data:
                slots = extract_slots(data)
                slot_lists.append(slots)

        # Determine the most complete slot list
        most_complete_list = get_most_complete_slot_list(slot_lists)

        # Cross-check slot availability
        missing_slots = cross_check_slots(most_complete_list, slot_lists)

        # Output the missing slots information
        print(json.dumps(missing_slots, indent=2))

        # Wait for 2 epochs
        time.sleep(EPOCH_DURATION * 2)

if __name__ == "__main__":
    main()
