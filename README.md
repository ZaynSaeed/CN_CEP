# ❄️ Smart Cold Storage Monitoring System (CEP)

## Project Overview
This project monitors temperature and humidity for a cold storage facility. It uses **MQTT** for real-time alerts and **HTTP** for reliable database logging.

## Technologies Used
* **Hardware:** ESP32 / ESP8266 (Simulated via Python)
* **Backend:** Python Flask
* **Database:** SQLite
* **Protocols:** MQTT (Live Stream) & HTTP (Periodic Log)
* **Frontend:** HTML5, CSS3, Chart.js

## How to Run

1.  **Install Dependencies:**
    ```bash
    pip install flask flask-cors paho-mqtt
    ```

2.  **Start the Server:**
    ```bash
    python server.py
    ```

3.  **Run Simulation (in separate terminals):**
    * `python fake_mqtt.py` (For Live Data)
    * `python fake_http.py` (For Database Logging)

4.  **Open Dashboard:**
    Go to http://localhost:5000
