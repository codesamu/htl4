
import cv2
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk
import random
import math

# ---- Hand Tracking ----
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)

# ---- Tkinter Setup ----
root = tk.Tk()
root.title("Hand Fruit Ninja with Bombs")

canvas_width = 640
canvas_height = 480
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack()

# ---- Game Variables ----
gravity = 0.5
spawn_interval = 2000  # milliseconds
fruit_radius = 20
fruits = []
score = 0

# Background
background_imgtk = None
background_canvas = canvas.create_image(0, 0, anchor="nw")

# Score display
score_text = canvas.create_text(10, 10, anchor="nw", text=f"Score: {score}", fill="white", font=("Arial", 20))

# ---- Fruit Class ----
class Fruit:
    def __init__(self):
        self.x = random.randint(fruit_radius, canvas_width - fruit_radius)
        self.y = canvas_height + fruit_radius
        self.vx = random.uniform(-4, 4)
        self.vy = -random.uniform(15, 25)  # higher jump
        self.is_bomb = random.random() < 0.2  # 20% chance of bomb
        self.color = "red" if self.is_bomb else "green"
        self.id = canvas.create_oval(
            self.x - fruit_radius, self.y - fruit_radius,
            self.x + fruit_radius, self.y + fruit_radius,
            fill=self.color
        )
        self.sliced = False

    def update(self):
        self.vy += gravity
        self.x += self.vx
        self.y += self.vy
        canvas.coords(
            self.id,
            self.x - fruit_radius, self.y - fruit_radius,
            self.x + fruit_radius, self.y + fruit_radius
        )

    def off_screen(self):
        return self.y - fruit_radius > canvas_height

# ---- Hand Detection ----
def get_hand_tip(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        tip = hand_landmarks.landmark[8]  # index fingertip
        x = int(tip.x * canvas_width)
        y = int(tip.y * canvas_height)
        return (x, y)
    return None

# ---- Fruit Spawning ----
def spawn_fruit():
    for _ in range(random.randint(1, 3)):  # spawn 1-3 fruits at a time
        fruits.append(Fruit())
    root.after(spawn_interval, spawn_fruit)

# ---- Update Game ----
def update_game():
    global background_imgtk, score

    ret, frame = cap.read()
    if not ret:
        root.after(10, update_game)
        return

    frame = cv2.flip(frame, 1)

    # ---- Background ----
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    background_imgtk = ImageTk.PhotoImage(image=img)
    canvas.itemconfig(background_canvas, image=background_imgtk)

    # ---- Hand Position ----
    hand = get_hand_tip(frame)
    if hand:
        # Draw a small yellow circle that fades away
        circle_id = canvas.create_oval(hand[0]-5, hand[1]-5, hand[0]+5, hand[1]+5, fill="yellow", outline="")
        root.after(300, lambda cid=circle_id: canvas.delete(cid))

    # ---- Update Fruits ----
    for fruit in fruits[:]:
        fruit.update()

        # Slice detection
        if hand:
            dx = fruit.x - hand[0]
            dy = fruit.y - hand[1]
            distance = math.hypot(dx, dy)
            if distance < fruit_radius + 10 and not fruit.sliced:
                fruit.sliced = True
                # Effect: change color to show sliced
                new_color = "darkred" if fruit.is_bomb else "lightgreen"
                canvas.itemconfig(fruit.id, fill=new_color)
                # Update score
                if fruit.is_bomb:
                    score = max(0, score - 1)  # subtract 1, don't go below 0
                else:
                    score += 1
                canvas.itemconfig(score_text, text=f"Score: {score}")
                # Remove fruit after short delay
                root.after(200, lambda f=fruit: remove_fruit(f))

        # Remove if off-screen
        if fruit.off_screen():
            remove_fruit(fruit)

    root.after(30, update_game)

def remove_fruit(fruit):
    if fruit in fruits:
        canvas.delete(fruit.id)
        fruits.remove(fruit)

def on_close():
    cap.release()
    hands.close()
    root.destroy()

# ---- Start Game ----
root.protocol("WM_DELETE_WINDOW", on_close)
spawn_fruit()
update_game()
root.mainloop()

