/*
  ============================================================
  RainMaker – Zone 1 Sensor Node
  Arduino Uno R4 WiFi

  Reads a soil moisture sensor and POSTs JSON readings to
  the FastAPI backend every 10 seconds.

  ─── EDUROAM NOTE ───────────────────────────────────────────
  Eduroam uses WPA2-Enterprise (802.1X). The R4 WiFi library
  only supports WPA2-Personal (PSK), so it CANNOT join eduroam
  directly.

  ✅ Fix: Hotspot your phone, connect BOTH your laptop and
     this Arduino to the hotspot. Everything works perfectly.
     Find your laptop's hotspot IP with:
       Windows → ipconfig  (look for Wi-Fi adapter IPv4)
       Mac/Linux → ifconfig / ip a

  ─── WIRING ─────────────────────────────────────────────────
  Moisture sensor SIG → A0
  Moisture sensor VCC → D7  (digital pin used as switched
                              power to prevent probe corrosion)
  Moisture sensor GND → GND

  ─── LIBRARIES NEEDED ───────────────────────────────────────
  • ArduinoJson  (search in Library Manager, by Benoit Blanchon)
  • WiFiS3       (included with the UNO R4 board package)
  ============================================================
*/

#include <WiFiS3.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include "Adafruit_VEML6070.h"

Adafruit_VEML6070 uv = Adafruit_VEML6070();

// ─── CONFIGURE THESE THREE LINES ──────────────────────────
const char* WIFI_SSID     = "Hasan";      // <-- your phone hotspot name
const char* WIFI_PASSWORD = "Flytrap1234";  // <-- your phone hotspot password
const char* SERVER_HOST   = "172.20.10.2";          // <-- your laptop's IP on the hotspot
// ──────────────────────────────────────────────────────────

const int   SERVER_PORT   = 8000;
const char* SERVER_PATH   = "/readings/";

// Zone 1 plot UUID — must match your Supabase plots table
const char* PLOT_ID = "950b5dd5-c2e6-4aeb-b2d0-8cf5b89c033e";

// Sensor pins
const int SOIL_SIG   = A0;
const int SOIL_POWER = 7;

// Send interval
const unsigned long SEND_INTERVAL = 10000;

WiFiClient client;
unsigned long lastSendTime = 0;

// ─── WIFI ─────────────────────────────────────────────────
void connectWiFi() {
  Serial.print("\nConnecting to: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n WiFi connected!");
    Serial.print("   Arduino IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("   Posting to: http://");
    Serial.print(SERVER_HOST);
    Serial.println(SERVER_PATH);
  } else {
    Serial.println("\n WiFi connection failed.");
    Serial.println("   Make sure WIFI_SSID/PASSWORD are correct.");
    Serial.println("   Eduroam won't work, use a phone hotspot.");
    Serial.println("   Retrying in 10 seconds...");
  }
}

// ─── READ SOIL MOISTURE ───────────────────────────────────
int readSoil() {
  digitalWrite(SOIL_POWER, HIGH); // Power the probe
  delay(10);                      // Brief settle time
  int raw = analogRead(SOIL_SIG);
  digitalWrite(SOIL_POWER, LOW);  // Power off (reduces corrosion)

  // Map raw ADC (0-1023) to 0-100% moisture.
  // Typical resistive sensor: ~900 = dry air, ~200 = submerged in water.
  // CALIBRATE: open Serial Monitor, hold sensor in dry soil and note the
  // raw value, then wet soil. Replace 900 and 200 with your readings.
  int moisture = map(raw, 900, 200, 0, 100);
  return constrain(moisture, 0, 100);
}

// ─── HTTP POST ────────────────────────────────────────────
void postReading(int moisture, int light) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi lost, reconnecting...");
    connectWiFi();
    if (WiFi.status() != WL_CONNECTED) return;
  }

  // Build JSON payload
  StaticJsonDocument<200> doc;
  doc["plot_id"]  = PLOT_ID;
  doc["moisture"] = moisture;
  doc["light"]    = light; // No light sensor attached, sends 0.
                        // If you wire one up: replace with analogRead(LIGHT_PIN)
  String body;
  serializeJson(doc, body);

  Serial.print("\nPOST moisture: ");
  Serial.print(moisture);
  Serial.println("%");

  Serial.print("\nPOST light: ");
  Serial.println(light);

  if (!client.connect(SERVER_HOST, SERVER_PORT)) {
    Serial.println("Cannot reach server.");
    Serial.println("   Check SERVER_HOST is your laptop's hotspot IP.");
    Serial.println("   Check FastAPI is running (uvicorn app.main:app).");
    return;
  }

  // HTTP/1.0 avoids chunked transfer encoding
  client.println("POST " + String(SERVER_PATH) + " HTTP/1.0");
  client.println("Host: " + String(SERVER_HOST));
  client.println("Content-Type: application/json");
  client.println("Connection: close");
  client.print("Content-Length: ");
  client.println(body.length());
  client.println();
  client.print(body);

  // Wait for response
  unsigned long t = millis();
  while (client.available() == 0 && millis() - t < 5000);

  if (client.available()) {
    String status = client.readStringUntil('\n');
    Serial.print("Server: ");
    Serial.println(status);
    if (status.indexOf("200") > 0) {
      Serial.println("Reading accepted.");
    } else {
      Serial.println("Unexpected response, check backend logs.");
    }
  } else {
    Serial.println("No response from server (timeout).");
  }

  client.stop();
}

// ─── SETUP ────────────────────────────────────────────────
void setup() {
  Serial.begin(9600);
  uv.begin(VEML6070_1_T);  // pass in the integration time constant for light
  while (!Serial && millis() < 3000);

  pinMode(SOIL_POWER, OUTPUT);
  digitalWrite(SOIL_POWER, LOW);

  connectWiFi();
}

// ─── LOOP ─────────────────────────────────────────────────
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
    delay(5000);
    return;
  }

  if (millis() - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = millis();
    int moisture = readSoil();
    int light = uv.readUV();
    postReading(moisture, light);
  }
}
