#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>

// ==========================================
// ⚠️ YOU MUST CHANGE THESE 4 LINES
// ==========================================
const char* ssid = "YOUR_WIFI_NAME";         // Enter your Wi-Fi Name
const char* password = "YOUR_WIFI_PASSWORD"; // Enter your Wi-Fi Password

// Find this by typing 'ipconfig' (Windows) or 'hostname -I' (Linux) in your terminal
const char* mqtt_server = "192.168.1.XX";    // Your Laptop's IP Address
String server_url = "http://192.168.1.XX:5000/sensor-data"; // Your Laptop's IP
// ==========================================

#define DHTPIN D2     // Pin where DHT11 is connected (GPIO 4)
#define DHTTYPE DHT11 // Sensor Type

WiFiClient espClient;
PubSubClient client(espClient);
HTTPClient http;
DHT dht(DHTPIN, DHTTYPE);

unsigned long lastHttpTime = 0;
const long httpInterval = 10000; // Send HTTP every 10 seconds

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a unique client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  // 1. Maintain MQTT Connection
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // 2. Read Sensor Data
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Check if reading failed
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // -------------------------------------------------
  // PROTOCOL 1: MQTT (REAL-TIME) - Sends every loop
  // -------------------------------------------------
  // JSON Format: {"unit_id": 1, "unit_name": "Milk Storage", "temperature": 25.5, "humidity": 60.0}
  String mqtt_payload = "{\"unit_id\": 1, \"unit_name\": \"Milk Storage\", \"temperature\": " + String(t) + ", \"humidity\": " + String(h) + "}";
  
  client.publish("coldstorage/live", mqtt_payload.c_str());
  Serial.println("MQTT Sent: " + mqtt_payload);


  // -------------------------------------------------
  // PROTOCOL 2: HTTP (LOGGING) - Sends every 10 sec
  // -------------------------------------------------
  unsigned long currentMillis = millis();
  if (currentMillis - lastHttpTime >= httpInterval) {
    lastHttpTime = currentMillis;
    
    WiFiClient client; // Create a WiFiClient for HTTP
    if (http.begin(client, server_url)) {
      http.addHeader("Content-Type", "application/json");
      
      // Note: ESP8266 doesn't know real time without NTP, so we send a generic timestamp string.
      // Ideally, the server should assign the time, but your code expects it in the JSON.
      String http_payload = "{\"unit_id\": 1, \"unit_name\": \"Milk Storage\", \"temperature\": " + String(t) + ", \"humidity\": " + String(h) + ", \"timestamp\": \"Hardware-Live\"}";
      
      int httpCode = http.POST(http_payload);
      
      if (httpCode > 0) {
        Serial.printf("HTTP Sent. Response: %d\n", httpCode);
      } else {
        Serial.printf("HTTP Failed. Error: %s\n", http.errorToString(httpCode).c_str());
      }
      http.end();
    } else {
      Serial.println("Unable to connect to Server URL");
    }
  }
  
  delay(2000); // Wait 2 seconds before next reading
}