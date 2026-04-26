import face_recognition
import cv2
import pickle
import requests

ESP32_IP = "http://192.168.1.100/unlock" 

ENCODINGS_FILE = "encodings.pickle"

with open(ENCODINGS_FILE, "rb") as f:
    data = pickle.load(f)

video_capture = cv2.VideoCapture(0)

last_unlocked = False  # prevent multiple requests

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

        # 🔓 Unlock if recognized
        if name != "Unknown" and not last_unlocked:
            try:
                requests.get(ESP32_IP)
                print("Door Unlock Triggered!")
                last_unlocked = True
            except:
                print("ESP32 not reachable")

        if name == "Unknown":
            last_unlocked = False

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()
