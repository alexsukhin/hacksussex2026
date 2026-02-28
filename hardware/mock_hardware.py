import requests
import time
import random
import uuid

# Configuration
BACKEND_URL = "http://127.0.0.1:8000/readings/"
SLEEP_INTERVAL = 5 # Send data every 5 seconds

# Generate 4 static UUIDs to represent our 4 physical zones/sensors
# We keep these static so the frontend can group data by zone
ZONES = {
    "Zone 1 (Arduino)": "8b3e3560-cb9d-4ebf-8571-d69a2191bbfa",
    "Zone 2 (Mock)": "bef10565-2068-4d00-8c89-1e79f359048b",
    "Zone 3 (Mock)": "27afa7d4-1a5c-451a-b72b-c70a60e4eb5d",
    "Zone 4 (Mock)": "28b31c76-7597-4206-ab54-b004f122b022",
}

def generate_mock_data():
    """Generates a random payload matching your ReadingCreate schema"""
    print("🌱 Starting Orchard Mock Hardware...")
    
    while True:
        for zone_name, plot_id in ZONES.items():
            # Generate random realistic data
            payload = {
                "plot_id": plot_id,  # <--- CHANGE THIS KEY to "plot_id"
                "moisture": random.randint(10, 95)
            }

            try:
                response = requests.post(BACKEND_URL, json=payload)
                if response.status_code == 200:
                    print(f"✅ Sent data for {zone_name}: {payload}")
                else:
                    print(f"⚠️ Failed to send {zone_name}. Status: {response.status_code}. Response: {response.text}")
            except requests.exceptions.ConnectionError:
                print("❌ Connection refused. Is your FastAPI backend running?")

        print(f"Sleeping for {SLEEP_INTERVAL} seconds...\n")
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    # To test this, make sure your FastAPI app is running first!
    generate_mock_data()