#include <WiFiS3.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include "Adafruit_VEML6070.h"

Adafruit_VEML6070 uv = Adafruit_VEML6070();

const char* WIFI_SSID     = "Hasan";      // hotspot
const char* WIFI_PASSWORD = "Flytrap1234";  // password
const char* SERVER_HOST   = "172.20.10.2";          // laptop id on hotspot
// ──────────────────────────────────────────────────────────

const int   SERVER_PORT   = 8000;
const char* SERVER_PATH   = "/readings/";

// Zone 1 plot UUID — must match your Supabase plots table
const char* PLOT_ID = "950b5dd5-c2e6-4aeb-b2d0-8cf5b89c033e";

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
  }
}

float mapMoistureExp(int raw) {
    // Clamp to calibration bounds first
    raw = constrain(raw, 27, 887);
    
    // Shift so raw starts at 1 (log(0) is undefined)
    float shifted     = raw - 27 + 1;
    float shiftedMax  = 887 - 27 + 1;
    
    // Log correction flattens the exponential curve
    float logVal      = log(shifted);
    float logMax      = log(shiftedMax);
    
    // Map to 0-100%
    float moisture    = (logVal / logMax) * 100.0;
    return constrain(moisture, 0.0, 100.0);
}

// ─── READ SOIL MOISTURE ───────────────────────────────────
int readSoil() {
  digitalWrite(SOIL_POWER, HIGH); // Power the probe
  delay(10);                      // Brief settle time
  int raw = analogRead(SOIL_SIG);
  digitalWrite(SOIL_POWER, LOW);  // Power off (reduces corrosion)

  int moisture = (int) mapMoistureExp(raw);
  Serial.println(raw);

  return moisture;
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
