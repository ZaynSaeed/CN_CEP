import time
import random
import json
import paho.mqtt.client as mqtt
from datetime import datetime

BROKER = "localhost"
PORT = 1883
TOPIC = "coldstorage/live"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)
client.loop_start()

print("📡 Fake sensor streaming via MQTT...")

while True:
    # ---- UNIT 1: MILK STORAGE ----
    milk_data = {
        "unit_id": 1,
        "unit_name": "Milk Storage",
        "temperature": round(random.uniform(2, 6), 2),
        "humidity": round(random.uniform(70, 85), 2),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    client.publish(TOPIC, json.dumps(milk_data))
    print("Sent (MQTT):", milk_data)

    time.sleep(1)

    # ---- UNIT 2: FROZEN STORAGE ----
    frozen_data = {
        "unit_id": 2,
        "unit_name": "Frozen Food Storage",
        "temperature": round(random.uniform(-10, -2), 2),
        "humidity": round(random.uniform(60, 75), 2),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    client.publish(TOPIC, json.dumps(frozen_data))
    print("Sent (MQTT):", frozen_data)

    time.sleep(2)
