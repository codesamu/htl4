import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np

# ---- MediaPipe Hands ----
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# ---- OpenCV Face Detection ----
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# ---- Age Detection Model ----
AGE_BUCKETS = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
age_net = cv2.dnn.readNetFromCaffe("age_deploy.prototxt", "age_net.caffemodel")

# ---- Camera ----
cap = cv2.VideoCapture(0)

# ---- Tkinter Setup ----
root = tk.Tk()
root.title("Face + Hand + Age Detection")

label = tk.Label(root)
label.pack()

# ---- Toggle Buttons ----
face_enabled = tk.BooleanVar(value=True)
hand_enabled = tk.BooleanVar(value=True)
controls = ttk.Frame(root, padding=10)
controls.pack()
ttk.Checkbutton(controls, text="Face Detection", variable=face_enabled).grid(row=0, column=0, padx=5)
ttk.Checkbutton(controls, text="Hand Detection", variable=hand_enabled).grid(row=0, column=1, padx=5)

# ---- MediaPipe Hands ----
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ---- Finger Counting ----
TIP_IDS = [4, 8, 12, 16, 20]

def count_fingers(hand_landmarks):
    fingers = []

    # Thumb
    if hand_landmarks.landmark[TIP_IDS[0]].x < hand_landmarks.landmark[TIP_IDS[0]-1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for id in range(1, 5):
        if hand_landmarks.landmark[TIP_IDS[id]].y < hand_landmarks.landmark[TIP_IDS[id]-2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return sum(fingers)

def gesture_name(finger_count):
    if finger_count == 0: return "Fist 👊"
    elif finger_count == 1: return "One ✋"
    elif finger_count == 2: return "Peace ✌️"
    elif finger_count == 3: return "Three 🤟"
    elif finger_count == 4: return "Four 🖐️"
    elif finger_count == 5: return "Open Hand 🖐️"
    return ""

# ---- Age Detection ----
def predict_age(face_roi):
    blob = cv2.dnn.blobFromImage(face_roi, 1.0, (227,227),
                                 (78.4263377603, 87.7689143744, 114.895847746),
                                 swapRB=False)
    age_net.setInput(blob)
    preds = age_net.forward()
    return AGE_BUCKETS[preds[0].argmax()]

# ---- Main Loop ----
def update_frame():
    ret, frame = cap.read()
    if not ret:
        root.after(10, update_frame)
        return

    frame = cv2.flip(frame, 1)

    # Face Detection + Age
    if face_enabled.get():
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
            face_roi = frame[y:y+h, x:x+w]
            try:
                age = predict_age(face_roi)
                cv2.putText(frame, f"Age: {age}", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)
            except:
                pass

    # Hand Detection + Gesture
    if hand_enabled.get():
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
                fingers = count_fingers(hand_landmarks)
                gesture = gesture_name(fingers)
                cv2.putText(frame, f"Gesture: {gesture}", (10,50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    # Convert to Tkinter Image
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    imgtk = ImageTk.PhotoImage(Image.fromarray(img))
    label.imgtk = imgtk
    label.configure(image=imgtk)

    root.after(10, update_frame)

# ---- Clean Exit ----
def on_close():
    cap.release()
    hands.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
update_frame()
root.mainloop()

