#!/bin/bash

set -u

# CSV file containing playlist data
CSV_FILE="year_end_hot_100_playlists.csv"

if [[ ! -f "$CSV_FILE" ]]; then
    echo "Error: CSV file '$CSV_FILE' not found!"
    exit 1
fi

tail -n +2 "$CSV_FILE" | while IFS=',' read -r name id tracks snapshot_id
do
    # Extract decade from the first four characters of the name
    # This current script starts at 2003 since I ran into throttling issue!!!
    decade=$(echo "$name" | grep -o '^[0-9]\{4\}')

    # Ensure ID and decade are not empty and filter for years 2003 and earlier
    if [[ -z "$id" || -z "$decade" || "$decade" -gt 2003 ]]; then
        echo "Skipping entry after 2003: Name='$name', ID='$id', Decade='$decade'"
        continue
    fi


    # Ensure ID and decade are not empty
    if [[ -z "$id" || -z "$decade" ]]; then
        echo "Skipping invalid entry: Name='$name', ID='$id', Decade='$decade'"
        continue
    fi

    # Run the Python script with the extracted values
    echo "Processing: $name (ID: $id, Decade: $decade)"
    python scrape_decade_data.py -p "$id" -d "$decade"

    # Handle errors by skipping failed IDs
    if [[ $? -ne 0 ]]; then
        echo "Error processing playlist ID: $id, skipping..."
        continue
    fi

done
