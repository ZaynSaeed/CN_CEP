import pymysql
import json
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import paho.mqtt.client as mqtt

app = Flask(__name__)
CORS(app)

# --------------------
# MYSQL CONFIGURATION
# --------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "zainhonmein", 
    "database": "cold_storage_db",
    "cursorclass": pymysql.cursors.Cursor 
}

# --------------------
# GLOBAL STATE
# --------------------
latest_mqtt_data = {}       # Live data per unit
alert_history = []          # List to store alert logs
last_alert_time = {1: 0, 2: 0} # To prevent spamming alerts

# --------------------
# DATABASE SETUP
# --------------------
def init_db():
    # 1. Connect to MySQL Server (No Database selected yet)
    conn = pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    cursor = conn.cursor()
    
    # 2. Create Database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS cold_storage_db")
    
    # 3. Use the Database
    cursor.execute("USE cold_storage_db")
    
    # 4. Create Table (MySQL Syntax: INT AUTO_INCREMENT)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            unit_id INT,
            unit_name VARCHAR(255),
            temperature FLOAT,
            humidity FLOAT,
            timestamp VARCHAR(255)
        )
    """)
    conn.commit()
    conn.close()
    print("✅ MySQL Database 'cold_storage_db' and Table 'sensor_readings' ready.")

# Initialize DB on startup
init_db()

# --------------------
# CEP LOGIC (The Brain)
# --------------------
def process_event(data):
    global alert_history, last_alert_time

    unit_id = data["unit_id"]
    temp = data["temperature"]
    current_time = time.time()
    
    # Update Live Data
    latest_mqtt_data[unit_id] = data

    # RULE: Check Thresholds
    alert_msg = None
    if unit_id == 1 and temp > 5.0:
        alert_msg = f"Critical: Milk Storage High Temp ({temp}°C)"
    elif unit_id == 2 and temp > -5.0:
        alert_msg = f"Critical: Frozen Food Thawing ({temp}°C)"

    # LOGIC: Only log alert if 60 seconds have passed since last one (Anti-Spam)
    if alert_msg:
        if (current_time - last_alert_time.get(unit_id, 0)) > 60:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = {"time": timestamp, "message": alert_msg, "unit": unit_id}
            
            # Add to history (Keep only last 50)
            alert_history.insert(0, log_entry) 
            if len(alert_history) > 50: alert_history.pop()
            
            last_alert_time[unit_id] = current_time
            print(f"🚨 ALERT LOGGED: {alert_msg}")

# --------------------
# MQTT HANDLERS
# --------------------
def on_mqtt_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        process_event(data)
    except Exception as e:
        print(f"MQTT Error: {e}")

def start_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    # Using Local Mosquitto
    try:
        client.connect("localhost", 1883, 60)
        client.subscribe("coldstorage/live")
        client.on_message = on_mqtt_message
        client.loop_forever()
    except Exception as e:
        print(f"⚠️ Could not connect to Mosquitto: {e}")
        print("Make sure Mosquitto is installed and running!")

# --------------------
# FLASK ROUTES
# --------------------
@app.route("/")
def index():
    return render_template("index.html")

# HTTP Logging (For Graph)
@app.route("/sensor-data", methods=["POST"])
def receive_data():
    data = request.json
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # MySQL Query uses %s placeholders instead of ?
        sql = "INSERT INTO sensor_readings (unit_id, unit_name, temperature, humidity, timestamp) VALUES (%s, %s, %s, %s, %s)"
        val = (data["unit_id"], data["unit_name"], data["temperature"], data["humidity"], data["timestamp"])
        
        cursor.execute(sql, val)
        conn.commit()
        conn.close()
        return jsonify({"status": "saved"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Graph History
@app.route("/history", methods=["GET"])
def history():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Fetch last 20 readings
        cursor.execute("SELECT unit_id, unit_name, temperature, humidity, timestamp FROM sensor_readings ORDER BY id DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()
        
        # Format for Frontend (Rows are tuples: (id, name, temp, hum, time))
        # Index: 0=unit_id, 1=unit_name, 2=temp, 3=humidity, 4=timestamp
        result = [{"unit_id": r[0], "temperature": r[2], "humidity": r[3], "timestamp": r[4]} for r in rows]
        
        return jsonify(result), 200
    except Exception as e:
        print(f"DB Error: {e}")
        return jsonify([]), 500

# Live Data + Alerts
@app.route("/live", methods=["GET"])
def live():
    return jsonify({
        "latest_data": latest_mqtt_data,
        "alerts": alert_history
    })

if __name__ == "__main__":
    mqtt_thread = threading.Thread(target=start_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()
    app.run(host="0.0.0.0", port=5000, debug=True)