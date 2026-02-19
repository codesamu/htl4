import tkinter as tk
from PIL import Image, ImageDraw
import numpy as np
import cv2

from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# ===============================
# PARAMETER
# ===============================
CANVAS_SIZE = 320          # Zeichenfläche
IMAGE_SIZE = 32            # CNN Input
MODEL_PATH = "handschrift_A_Z_model.h5"

# ===============================
# MODELL LADEN
# ===============================
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Modell-Datei nicht gefunden!")

model = load_model(MODEL_PATH)

# ===============================
# GUI SETUP
# ===============================
root = tk.Tk()
root.title("Handschrift A–Z – Live Erkennung")

# ===============================
# ZEICHENFLÄCHE
# ===============================
canvas = tk.Canvas(root, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white")
canvas.grid(row=0, column=0, padx=10, pady=10)

image = Image.new("L", (CANVAS_SIZE, CANVAS_SIZE), 255)  # Weißer Hintergrund
draw = ImageDraw.Draw(image)

last_x, last_y = None, None

def draw_line(event):
    global last_x, last_y
    if last_x is not None:
        canvas.create_line(
            last_x, last_y, event.x, event.y,
            width=8, fill="black", capstyle=tk.ROUND, smooth=True
        )
        draw.line(
            [last_x, last_y, event.x, event.y],
            fill=0, width=8  # Schwarz auf weiß
        )
        update_prediction()
    last_x, last_y = event.x, event.y

def reset_pos(event):
    global last_x, last_y
    last_x, last_y = None, None

canvas.bind("<B1-Motion>", draw_line)
canvas.bind("<ButtonRelease-1>", reset_pos)

# ===============================
# CLEAR BUTTON
# ===============================
def clear_canvas():
    canvas.delete("all")
    draw.rectangle([0, 0, CANVAS_SIZE, CANVAS_SIZE], fill=255)  # Weiß
    update_prediction()

btn_clear = tk.Button(root, text="Clear", command=clear_canvas)
btn_clear.grid(row=1, column=0, pady=5)

# ===============================
# MATPLOTLIB DIAGRAMM
# ===============================
fig, ax = plt.subplots(figsize=(6,4))
bars = ax.bar([chr(i + ord('A')) for i in range(26)], np.zeros(26))
ax.set_ylim(0, 100)
ax.set_ylabel("Wahrscheinlichkeit [%]")
ax.set_title("A–Z Wahrscheinlichkeiten")

fig.tight_layout()

chart = FigureCanvasTkAgg(fig, master=root)
chart.get_tk_widget().grid(row=0, column=1, rowspan=2, padx=10, pady=10)

# ===============================
# VORHERSAGE
# ===============================
def update_prediction():
    img = image.resize((IMAGE_SIZE, IMAGE_SIZE))
    img = np.array(img, dtype=np.float32) / 255.0
    img = img.reshape(1, IMAGE_SIZE, IMAGE_SIZE, 1)

    prediction = model.predict(img, verbose=0)[0] * 100

    for bar, prob in zip(bars, prediction):
        bar.set_height(prob)

    best_idx = np.argmax(prediction)
    ax.set_title(f"Erkannt: {chr(best_idx + ord('A'))}")

    chart.draw()

# Initiale Anzeige
update_prediction()

# ===============================
# START GUI
# ===============================
root.mainloop()