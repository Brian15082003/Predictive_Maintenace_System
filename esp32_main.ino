/**
 * ESP32 Main Firmware - IoT Predictive Maintenance System
 * 
 * Handles:
 *  - DHT11: Ambient temperature and humidity (digital, single-wire)
 *  - ADXL345: 3-axis vibration (I2C: SDA=GPIO21, SCL=GPIO22)
 *  - Wi-Fi: HTTP POST to Flask server every 2 seconds
 *  - Alerts: LED dome + Buzzer when 90% threshold crossed
 *  - ThingSpeak: Cloud data logging
 * 
 * Authors: Brian Dias, Sheshank Naik, Steve Bernard, Valois Fernandes
 * Institution: Goa College of Engineering, 2024-2025
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
#include <Arduino.h>

// ── Pin Definitions ─────────────────────────────────────────────
#define DHT_SENSOR_PIN    4     // DHT11 data pin
#define DHT_SENSOR_TYPE   DHT11
#define LED_ALERT_PIN     2     // Red LED dome indicator
#define BUZZER_PIN        15    // Active buzzer

// ── Threshold Values (90% of safe operating limits) ─────────────
#define TEMP_THRESHOLD    63.0  // 90% of 70°C
#define VIBRATION_THRESH  1.80  // 90% of ±2g
#define CURRENT_THRESH    8.0   // 90% of 8.7A max

// ── Network Configuration ───────────────────────────────────────
const char* ssid       = "YOUR_WIFI_SSID";
const char* password   = "YOUR_WIFI_PASSWORD";
const char* server     = "http://192.168.1.100:5000"; // Flask server IP

// ThingSpeak
const char* thingspeakServer = "http://api.thingspeak.com/update";
const char* apiKey           = "YOUR_THINGSPEAK_API_KEY";

// ── Object Initialization ────────────────────────────────────────
DHT dht_sensor(DHT_SENSOR_PIN, DHT_SENSOR_TYPE);
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified();
sensors_event_t event;

// ── Setup ────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);

  // Pin modes
  pinMode(LED_ALERT_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(LED_ALERT_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  // Initialize DHT11
  dht_sensor.begin();
  Serial.println("DHT11 initialized.");

  // Initialize ADXL345
  if (!accel.begin()) {
    Serial.println("ERROR: ADXL345 not detected. Check wiring!");
    while (1);  // Halt
  }
  accel.setRange(ADXL345_RANGE_2_G);
  Serial.println("ADXL345 initialized at ±2g range.");

  // Connect to Wi-Fi
  Serial.print("Connecting to Wi-Fi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

// ── Threshold Check & Local Alert ───────────────────────────────
void triggerLocalAlert(bool alertActive) {
  if (alertActive) {
    digitalWrite(LED_ALERT_PIN, HIGH);
    digitalWrite(BUZZER_PIN, HIGH);
  } else {
    digitalWrite(LED_ALERT_PIN, LOW);
    digitalWrite(BUZZER_PIN, LOW);
  }
}

// ── Send Data to Flask Server ────────────────────────────────────
void sendToFlask(float temp, float humid, float x, float y, float z) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(server) + "/data");
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{";
    jsonPayload += "\"temperature\": " + String(temp)  + ", ";
    jsonPayload += "\"humidity\": "    + String(humid) + ", ";
    jsonPayload += "\"X axis\": "      + String(x)     + ", ";
    jsonPayload += "\"Y axis\": "      + String(y)     + ", ";
    jsonPayload += "\"Z axis\": "      + String(z)     + "}";

    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Flask response: " + response);
    } else {
      Serial.println("Error sending data to Flask. Code: " + String(httpResponseCode));
    }
    http.end();
  }
}

// ── Send Data to ThingSpeak ──────────────────────────────────────
void sendToThingSpeak(float temp, float humid, float x, float y, float z) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(thingspeakServer)
               + "?api_key=" + apiKey
               + "&field1="  + String(temp)
               + "&field2="  + String(humid)
               + "&field3="  + String(x)
               + "&field4="  + String(y)
               + "&field5="  + String(z);

    http.begin(url);
    int httpCode = http.GET();
    if (httpCode > 0) {
      Serial.println("ThingSpeak updated successfully.");
    } else {
      Serial.println("ThingSpeak error: " + String(httpCode));
    }
    http.end();
  }
}

// ── Receive Command from Flask ────────────────────────────────────
void receiveCommand() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(server) + "/command");
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Command from server: " + response);
      // Add command handling logic here (e.g., parse JSON action)
    } else {
      Serial.println("Error getting command.");
    }
    http.end();
  }
}

// ── Main Loop ────────────────────────────────────────────────────
void loop() {
  // 1. Read DHT11
  float temp  = dht_sensor.readTemperature();
  float humid = dht_sensor.readHumidity();

  // 2. Read ADXL345 vibration
  accel.getEvent(&event);
  float x = event.acceleration.x;
  float y = event.acceleration.y;
  float z = event.acceleration.z;

  // 3. Print to Serial Monitor
  Serial.print("Temp: ");    Serial.print(temp);  Serial.print("°C | ");
  Serial.print("Humid: ");   Serial.print(humid); Serial.print("% | ");
  Serial.print("X: ");       Serial.print(x);     Serial.print(" | ");
  Serial.print("Y: ");       Serial.print(y);     Serial.print(" | ");
  Serial.print("Z: ");       Serial.println(z);

  // 4. Check thresholds → trigger local alert
  bool alertActive = (temp  >= TEMP_THRESHOLD)     ||
                     (abs(x) >= VIBRATION_THRESH)  ||
                     (abs(y) >= VIBRATION_THRESH)  ||
                     (abs(z) >= VIBRATION_THRESH);
  triggerLocalAlert(alertActive);

  if (alertActive) {
    Serial.println("⚠️  THRESHOLD BREACH DETECTED — Alert triggered!");
  }

  // 5. Small delay before HTTP calls
  delay(100);

  // 6. Send to Flask server
  sendToFlask(temp, humid, x, y, z);

  // 7. Send to ThingSpeak (every 15 seconds recommended to avoid rate limiting)
  static unsigned long lastThingSpeak = 0;
  if (millis() - lastThingSpeak > 15000) {
    sendToThingSpeak(temp, humid, x, y, z);
    lastThingSpeak = millis();
  }

  // 8. Receive command from server
  receiveCommand();

  // 9. Wait before next cycle
  delay(2000);
}
