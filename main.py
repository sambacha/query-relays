#!/usr/bin/env python3
"""
  Query MEV Relay Endpoints for Available Slots
  Reduce to see which slots are not available
  
  Saves output in format:
    
    [relay, [slot1,...,slotn+1]]
    titanrelay.xyz,"9278499,9278503,9278504,9278505,9278506,9278510,9278523,9278529,9278533,9278542,9278543,9278556"

NOTE: This doesn't check against all 64 slots
"""
import requests
import csv
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log_filename = f"relay_slots_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
csv_filename = f"relay_slots_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# List of MEV relay URLs
relays = [
    "https://0xa1559ace749633b997cb3fdacffb890aeebdb0f5a3b6aaa7eeeaf1a38af0a8fe88b9e4b1f61f236d2e64d95733327a62@relay.ultrasound.money",
    "https://0x8c4ed5e24fe5c6ae21018437bde147693f68cda427cd1122cf20819c30eda7ed74f72dece09bb313f2a1855595ab677d@titanrelay.xyz",
]

MAX_SLOTS = 64

def fetch_relay_slots(relay_url):
    try:
        response = requests.get(f"{relay_url}/relay/v1/builder/validators")
        response.raise_for_status()
        data = response.json()
        slots = [entry['slot'] for entry in data][:MAX_SLOTS]
        assert slots, f"No slots returned by {relay_url}"
        return slots
    except requests.RequestException as e:
        logging.error(f"Failed to fetch data from {relay_url}: {e}")
        return []
    except AssertionError as e:
        logging.error(e)
        return []

def log_and_save_slots(relay_slots):
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Relay URL', 'Slots'])
        for relay, slots in relay_slots.items():
            logging.info(f"Slots for {relay}: {slots}")
            writer.writerow([relay, ','.join(slots)])

def main():
    relay_slots = {}
    for relay in relays:
        slots = fetch_relay_slots(relay)
        relay_slots[relay] = slots

    # Filter out relays that returned no slots
    relay_slots = {k: v for k, v in relay_slots.items() if v}

    # If no relay returned slots, exit early
    if not relay_slots:
        logging.error("No slots were returned by any relay.")
        return

    max_slots_relay = max(relay_slots, key=lambda k: len(relay_slots[k]))
    reference_slots = set(relay_slots[max_slots_relay])

    missing_slots = {}
    for relay, slots in relay_slots.items():
        if relay != max_slots_relay:
            missing = reference_slots - set(slots)
            missing_slots[relay] = list(missing)

    for relay, missing in missing_slots.items():
        logging.info(f"Missing slots in {relay}: {missing}")

    log_and_save_slots(relay_slots)

if __name__ == "__main__":
    main()