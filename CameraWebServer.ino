#include <WiFi.h>
#include <ESPAsyncWebServer.h>

const char* ssid = "AO3";
const char* password = "a12b32";

const int relayPin = 2;

AsyncWebServer server(80);

void setup() {
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
  }

  server.on("/unlock", HTTP_GET, [](AsyncWebServerRequest *request){
    digitalWrite(relayPin, LOW);
    delay(5000);
    digitalWrite(relayPin, HIGH);
    request->send(200, "text/plain", "Door Unlocked");
  });

  server.begin();
}

void loop() {}
