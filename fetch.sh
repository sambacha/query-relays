#!/bin/bash

# List of MEV relay URLs
relays=(
    "https://0xa1559ace749633b997cb3fdacffb890aeebdb0f5a3b6aaa7eeeaf1a38af0a8fe88b9e4b1f61f236d2e64d95733327a62@relay.ultrasound.money" "https://0x8c4ed5e24fe5c6ae21018437bde147693f68cda427cd1122cf20819c30eda7ed74f72dece09bb313f2a1855595ab677d@titanrelay.xyz"
)

# Maximum number of slots to consider
MAX_SLOTS=64

# Directory to store the CSV files
OUTPUT_DIR="relay_slots"
mkdir -p $OUTPUT_DIR

# Function to fetch slots from a relay and save to CSV
fetch_relay_slots() {
    relay_url=$1
    relay_name=$(echo $relay_url | awk -F/ '{print $3}')
    output_file="${OUTPUT_DIR}/${relay_name}.csv"

    echo "Fetching slots from ${relay_url}..."

    response=$(curl -s "$relay_url/relay/v1/builder/validators")

    if [ $? -ne 0 ]; then
        echo "Failed to fetch data from ${relay_url}"
        return
    fi

    echo "$response" | jq -r '[.[] | {slot: .slot}] | (["slot"] | @csv), (.[] | [.slot] | @csv)' | head -n $((MAX_SLOTS + 1)) > $output_file
}

# Fetch slots for each relay
for relay in "${relays[@]}"; do
    fetch_relay_slots $relay
done

# Find the relay with the maximum slots
max_slots_relay=""
max_slots=0

for file in $OUTPUT_DIR/*.csv; do
    slots=$(wc -l < $file)
    if [ $slots -gt $max_slots ]; then
        max_slots=$slots
        max_slots_relay=$file
    fi
done

echo "Relay with the maximum slots: $max_slots_relay"

# Find missing slots in other relays
for file in $OUTPUT_DIR/*.csv; do
    if [ "$file" != "$max_slots_relay" ]; then
        relay_name=$(basename $file .csv)
        echo "Missing slots in ${relay_name}:"
        mlr --csv join --ul -j slot -f $max_slots_relay -n $file | mlr --csv filter '$slot==""' | mlr --csv cut -f slot
    fi
done
