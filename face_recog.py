import pandas as pd
import cv2
import urllib.request
import numpy as np
import os
from datetime import datetime
import face_recognition

# === Configuration ===
image_folder = r'C:\Users\Farhana\Desktop\Faces'
url = 'http://192.168.115.95/cam-hi.jpg'  # Replace with your actual IP cam stream URL

# === Attendance CSV Setup ===
attendance_dir = os.path.join(os.getcwd(), 'attendance')
os.makedirs(attendance_dir, exist_ok=True)
attendance_file = os.path.join(attendance_dir, 'Attendance.csv')

# Reset attendance file if it exists, else create it
if os.path.exists(attendance_file):
    print("Existing Attendance.csv found. Removing it...")
    os.remove(attendance_file)

df = pd.DataFrame(columns=["Name", "Time"])
df.to_csv(attendance_file, index=False)
print("Attendance.csv initialized.")

# === Load Images and Encode Faces ===
images = []
classNames = []

print("Loading images...")
myList = os.listdir(image_folder)
for cl in myList:
    img_path = os.path.join(image_folder, cl)
    curImg = cv2.imread(img_path)
    if curImg is not None:
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
print(f"Loaded classes: {classNames}")

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            encodeList.append(encodings[0])
    return encodeList

def markAttendance(name):
    with open(attendance_file, 'r+') as f:
        myDataList = f.readlines()
        nameList = [line.split(',')[0] for line in myDataList]
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.write(f'\n{name},{dtString}')
            print(f"Attendance marked for {name} at {dtString}")

# Encode all known faces
encodeListKnown = findEncodings(images)
print('Encoding Complete.')

# === Main Webcam Feed Loop ===
print("Starting camera feed. Press 'q' to quit.")
while True:
    try:
        img_resp = urllib.request.urlopen(url)
        imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgnp, -1)
    except Exception as e:
        print(f"Error fetching camera frame: {e}")
        continue

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = [v * 4 for v in (y1, x2, y2, x1)]

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            markAttendance(name)

    cv2.imshow('Webcam', img)
    key = cv2.waitKey(5)
    if key == ord('q'):
        print("Exiting...")
        break

cv2.destroyAllWindows()