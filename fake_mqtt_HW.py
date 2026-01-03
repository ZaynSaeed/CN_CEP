import paho.mqtt.client as mqtt
import json
import time
import random

# CONFIGURATION
BROKER = "localhost"  
TOPIC = "coldstorage/live"

# SIMULATION CONFIG (Only Unit 2)
units = {

    2: {
        "name": "Frozen Food Storage",
        "temp_range": (-10, -2),  # Cold temps
        "hum_range": (60, 75)
    }
}

def on_connect(client, userdata, flags, rc, properties=None): # Added properties=None for protocol v5/v2 compatibility
    if rc == 0:
        print("✅ Connected to Mosquitto Broker!")
    else:
        print(f"⚠️ Failed to connect, return code {rc}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect

try:
    client.connect(BROKER, 1883, 60)
    client.loop_start()  # Start background thread

    while True:
        for unit_id, info in units.items():
            # Generate fake data
            payload = {
                "unit_id": unit_id,
                "unit_name": info["name"],
                "temperature": round(random.uniform(*info["temp_range"]), 2),
                "humidity": round(random.uniform(*info["hum_range"]), 2)
            }
            
            # Publish to Broker
            client.publish(TOPIC, json.dumps(payload))
            print(f"Published Unit {unit_id}: {payload['temperature']}°C")
        
        time.sleep(2)  # Send every 2 seconds

except Exception as e:
    print(f"Error: {e}")
    client.loop_stop()