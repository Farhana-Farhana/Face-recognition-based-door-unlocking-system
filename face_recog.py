import face_recognition
import cv2
import requests
import time

# Load the known image and extract face encoding
known_image_path = r"C:\Users\Farhana\Desktop\Faces\priyansh.jfif"
known_image = face_recognition.load_image_file(known_image_path)
known_encodings = face_recognition.face_encodings(known_image)

if len(known_encodings) == 0:
    print("❌ No faces found in the known image.")
    exit()

known_encoding = known_encodings[0]

# Webcam setup  u
video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not video.isOpened():
    print("❌ Could not open webcam.")
    exit()

print("✅ Webcam started. Beginning face recognition...")

last_unlock_time = 0
UNLOCK_COOLDOWN = 5  # seconds
TOLERANCE = 0.45     # Lower = stricter matching

while True:
    ret, frame = video.read()
    if not ret:
        print("❌ Failed to capture image.")
        break

    # Resize and convert to RGB
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_frame = small_frame[:, :, ::-1]

    # Detect faces
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare face with known face
        matches = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=TOLERANCE)
        face_distance = face_recognition.face_distance([known_encoding], face_encoding)[0]

        if matches[0]:
            label = "Authorized"
            print(f"✅ Face recognized (distance: {face_distance:.2f}).")

            # Cooldown logic
            current_time = time.time()
            if current_time - last_unlock_time > UNLOCK_COOLDOWN:
                try:
                    response = requests.get("http://192.168.74.79/unlock")
                    print("🔓 Door Unlocked:", response.text)
                    last_unlock_time = current_time
                except Exception as e:
                    print(f"❌ Error: Could not connect to ESP32. {e}")
        else:
            label = "Unknown"
            print(f"❌ Unauthorized face detected (distance: {face_distance:.2f}).")

        # Scale back up face box since the frame was scaled down
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw box and label
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0) if matches[0] else (0, 0, 255), 2)
        cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Show the webcam feed
    cv2.imshow("Face Unlock", frame)

    # Exit on 'q' key
    if cv2.waitKey(10) & 0xFF == ord('q'):
        print("👋 Exiting...")
        break

video.release()
cv2.destroyAllWindows()
