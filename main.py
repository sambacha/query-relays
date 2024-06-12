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

def get_all_slots(relays):
    slots = {}
    for relay in relays:
        validators = get_validator_slots(relay)
        for entry in validators:
            slot = entry["slot"]
            validator = entry["validator"]
            if slot not in slots:
                slots[slot] = []
            slots[slot].append(validator)
    return slots

def find_missing_slots(all_slots, reference_slots):
    missing_slots = {}
    for slot in reference_slots:
        if slot not in all_slots:
            missing_slots[slot] = None
    return missing_slots

def cross_check_slots(relays):
    all_slots = {}
    for relay in relays:
        relay_slots = get_validator_slots(relay)
        for entry in relay_slots:
            slot = entry["slot"]
            if slot not in all_slots:
                all_slots[slot] = []
            all_slots[slot].append(relay)

    max_slots_relay = max(all_slots, key=lambda k: len(all_slots[k]))
    reference_slots = set(all_slots[max_slots_relay])
    
    missing_slots = {}
    for relay, slots in all_slots.items():
        missing_in_relay = find_missing_slots(reference_slots, set(slots))
        if missing_in_relay:
            missing_slots[relay] = missing_in_relay
    
    return missing_slots

def main():
    while True:
        print("Querying MEV Relays for validator slots...")
        missing_slots = cross_check_slots(mev_relays)
        
        for relay, slots in missing_slots.items():
            print(f"Missing slots in {relay}: {slots}")
        
        # Wait for 2 epochs (approximately 12.8 minutes in Ethereum 2.0)
        time.sleep(768)

if __name__ == "__main__":
    main()
