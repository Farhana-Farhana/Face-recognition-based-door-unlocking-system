#include <WiFi.h>
#include <ESPAsyncWebServer.h>

const char* ssid = "AO3";
const char* password = "a12b32";

AsyncWebServer server(80);
const int relayPin = 14;

unsigned long unlockStartTime = 0;
bool isUnlocked = false;

void setup() {
  Serial.begin(115200);

  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH); // Locked (active LOW relay)

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected!");
  Serial.println(WiFi.localIP());

  // Home route
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(200, "text/plain", "ESP32 Door Lock System Running");
  });

  // Unlock route
  server.on("/unlock", HTTP_GET, [](AsyncWebServerRequest *request){
    digitalWrite(relayPin, LOW); // Unlock
    unlockStartTime = millis();
    isUnlocked = true;

    request->send(200, "text/plain", "Door Unlocked");
  });

  server.begin();
}

void loop() {
  if (isUnlocked && millis() - unlockStartTime >= 3000) {
    digitalWrite(relayPin, HIGH); // Lock again
    isUnlocked = false;
    Serial.println("Door Locked");
  }
}
