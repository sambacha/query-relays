import requests

# List of MEV relay URLs
relays = [
    "https://0xa1559ace749633b997cb3fdacffb890aeebdb0f5a3b6aaa7eeeaf1a38af0a8fe88b9e4b1f61f236d2e64d95733327a62@relay.ultrasound.money",
    "https://0x8c4ed5e24fe5c6ae21018437bde147693f68cda427cd1122cf20819c30eda7ed74f72dece09bb313f2a1855595ab677d@titanrelay.xyz",
]

def fetch_relay_slots(relay_url):
    response = requests.get(f"{relay_url}/relay/v1/builder/validators")
    if response.status_code == 200:
        data = response.json()
        return [entry['slot'] for entry in data]
    else:
        print(f"Failed to fetch data from {relay_url}")
        return []

# Step 1: Fetch data from all relays
relay_slots = {}
for relay in relays:
    slots = fetch_relay_slots(relay)
    relay_slots[relay] = slots

# Step 2: Identify the relay with the maximum slots
max_slots_relay = max(relay_slots, key=lambda k: len(relay_slots[k]))
reference_slots = set(relay_slots[max_slots_relay])

# Step 3: Cross-check slots
missing_slots = {}
for relay, slots in relay_slots.items():
    if relay != max_slots_relay:
        missing = reference_slots - set(slots)
        missing_slots[relay] = list(missing)

# Output the results
for relay, missing in missing_slots.items():
    print(f"Missing slots in {relay}: {missing}")
