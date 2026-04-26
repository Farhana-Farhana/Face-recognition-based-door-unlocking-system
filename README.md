# 🔐 Face Recognition Door Unlocking System using ESP32-CAM

This project implements a **smart door unlocking system using facial recognition**. It eliminates the need for traditional keys by using **face detection and recognition** to grant access. The system captures a live image, compares it with stored faces, and unlocks the door if a match is found.

---

## 🎯 Objectives

* To develop a secure door access system using face recognition
* To eliminate physical keys and manual access
* To integrate ESP32-CAM with relay-controlled locking
* To implement real-time face detection and recognition

---

## ⚙️ Components Used

* ESP32-CAM
* FTDI Programmer
* Relay Module
* Solenoid Lock
* 12V Battery
* Jumper Wires
* Breadboard

---

## 🧠 Technologies Used

* Python
* OpenCV
* face_recognition library
* ESP32-CAM (WiFi-enabled microcontroller)

---

## 🔧 Working Principle

The system works by capturing a real-time image using ESP32-CAM and comparing it with stored images.

* Images of authorized users are stored in a folder
* Live image is captured and processed using Python
* Face encodings are generated and compared
* If a match is found → relay is activated → door unlocks
* After a few seconds → relay turns OFF → door locks again

👉 This ensures secure and automatic access control.

---

## 🔄 System Flow

Face Capture → Image Processing → Face Matching → ESP32 Trigger → Relay → Door Unlock

---

## 💻 Python Code (Face Recognition)

```python
import face_recognition
import cv2
import pickle
import requests
import time

ESP32_IP = "http://192.168.1.5/unlock"  

ENCODINGS_FILE = "encodings.pickle"

with open(ENCODINGS_FILE, "rb") as f:
    data = pickle.load(f)

video_capture = cv2.VideoCapture(0)

last_trigger_time = 0
cooldown = 5   # seconds (prevents multiple unlocks)

while True:
    ret, frame = video_capture.read()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(data["encodings"], face_encoding)
        name = "Unknown"

        if True in matches:
            matchedIdx = matches.index(True)
            name = data["names"][matchedIdx]

        print("Detected:", name)

        # 🔓 Unlock logic
        current_time = time.time()

        if name != "Unknown" and (current_time - last_trigger_time > cooldown):
            try:
                response = requests.get(ESP32_IP)
                print("Door Unlock Triggered!")
                print("ESP32 Response:", response.text)
                last_trigger_time = current_time
            except Exception as e:
                print("Error:", e)

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()
```

---

## 💻 ESP32-CAM Code (Relay Control)

```cpp
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
```

---

## 🔌 Hardware Connections

### 📷 ESP32-CAM + Relay

| Component | Connection |
| --------- | ---------- |
| Relay IN  | GPIO 4     |
| Relay VCC | 5V         |
| Relay GND | GND        |

---

### 🔐 Relay + Solenoid Lock

* Relay controls power to solenoid lock
* When relay ON → door unlocks
* When relay OFF → door locks

---

## 📸 Circuit Diagram

<p align="center">
  <img src="circuit.png" width="500"/>
</p>

---

## 📸 Prototype

<p align="center">
  <img src="prototype.png" width="500"/>
</p>

---

## 📊 Results

<p align="center">
  <img src="result.png" width="500"/>
</p>

* Authorized users were successfully recognized
* Door unlocked within **1–2 seconds**
* System automatically relocked after delay
* Continuous monitoring enabled real-time access

---

## ✅ Applications

* Smart home security
* Office access control
* Attendance systems
* Secure entry systems

---

## 🚀 Future Enhancements

* 📱 Mobile app integration
* 🔊 Buzzer alert for unknown faces
* ☁️ Cloud-based face database
* 📊 AI model improvement (CNN)

---

## 📚 Learning Outcomes

* Computer vision using OpenCV
* Face recognition techniques
* ESP32-CAM programming
* IoT-based automation
* Hardware + software integration

---

## 📚 Conclusion

This project demonstrates a secure and efficient door unlocking system using face recognition.
It combines embedded systems and AI to create a modern access control solution.
