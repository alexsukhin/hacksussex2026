import requests
import time
import random
import uuid

# Configuration
BACKEND_URL = "http://127.0.0.1:8000/readings/"
SLEEP_INTERVAL = 10 # Send data every 10 seconds

# Generate 4 static UUIDs to represent our 4 physical zones/sensors
# We keep these static so the frontend can group data by zone
ZONES = {
    # "Zone 1 (Arduino)": "950b5dd5-c2e6-4aeb-b2d0-8cf5b89c033e",
    "Zone 2 (Mock)": "03256848-ddcf-4e66-b122-30a4a0af27ac",
    "Zone 3 (Mock)": "4084dce6-1537-45e7-a435-05479b6c5263",
    "Zone 4 (Mock)": "f65f9eda-4f72-4273-bc83-014c6fc3a7d7",
    "Zone 5 (Mock)": "27b29098-ce21-4b11-b7e5-69d21fe96c92",
    "Zone 6 (Mock)": "ac02134e-594b-403f-a49d-164d04393b60",
    "Zone 7 (Mock)": "a72aa36a-757b-4132-b710-9dafb93ff030",
    "Zone 8 (Mock)": "b8a51a6b-e674-42c8-bdf6-029aa5e30c94",
    "Zone 9 (Mock)": "e6e36356-163d-4d79-ad3b-9a195cd6d5b8",
}

def generate_mock_data():
    """Generates a random payload matching your ReadingCreate schema"""
    print("🌱 Starting Orchard Mock Hardware...")
    
    while True:
        for zone_name, plot_id in ZONES.items():
            # Generate random realistic data
            payload = {
                "plot_id": plot_id,
                "moisture": random.randint(10, 95),
                "light": random.randint(200, 800) 
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