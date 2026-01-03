import random
import time
import requests
from datetime import datetime

SERVER_URL = "http://127.0.0.1:5000/sensor-data"

units = {
    2: {
        "name": "Frozen Food Storage",
        "temp_range": (-10, -2),
        "hum_range": (60, 75)
    }
}

while True:
    for unit_id, info in units.items():
        data = {
            "unit_id": unit_id,
            "unit_name": info["name"],
            "temperature": round(random.uniform(*info["temp_range"]), 2),
            "humidity": round(random.uniform(*info["hum_range"]), 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            response = requests.post(SERVER_URL, json=data)
            print(f"Sent Unit {unit_id}: {data['temperature']}C | Status: {response.status_code}")
        except:
            print("Server not running...")

    time.sleep(10)