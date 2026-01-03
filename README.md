# ❄️ Smart Cold Storage Monitoring System

## 🛠️ Prerequisites (Required Software)
Before running the project, you must install the following:

1.  **Python 3.x**
2.  **Mosquitto MQTT Broker** (The system will not work without this!)

### How to Install Mosquitto:
* **Windows:** Download and install from [mosquitto.org](https://mosquitto.org/download/). After installing, open a Command Prompt and type `net start mosquitto` to ensure it is running.
* **Linux (Ubuntu/Debian):** Run `sudo apt install mosquitto mosquitto-clients` and then `sudo systemctl start mosquitto`.
* **Mac:** Run `brew install mosquitto` and then `brew services start mosquitto`.

---

## 🚀 How to Run the Project

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/ZaynSaeed/CN_CEP.git](https://github.com/ZaynSaeed/CN_CEP.git)
    cd CN_CEP
    ```

2.  **Install Python Libraries:**
    ```bash
    pip install flask flask-cors paho-mqtt
    ```

3.  **Run the System (You need 3 Terminals):**

    * **Terminal 1 (The Server):**
        ```bash
        python server.py
        ```
    * **Terminal 2 (Database Logger):**
        ```bash
        python fake_http.py
        ```
    * **Terminal 3 (Live Stream):**
        ```bash
        python fake_mqtt.py
        ```

4.  **View Dashboard:**
    Open your browser and go to: `http://localhost:5000`
