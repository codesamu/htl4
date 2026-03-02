import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
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
# job id for a scheduled prediction; prevents calling prediction on every motion
timeout_job = None

def schedule_prediction():
    """Schedule prediction after short delay to keep drawing smooth."""
    global timeout_job
    if timeout_job is None:
        # schedule once, subsequent draw_line calls won't reschedule
        timeout_job = root.after(80, do_prediction)

def do_prediction():
    global timeout_job
    update_prediction()
    timeout_job = None

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
        schedule_prediction()
    last_x, last_y = event.x, event.y

def reset_pos(event):
    global last_x, last_y, timeout_job
    last_x, last_y = None, None
    # run prediction immediately when user stops drawing
    if timeout_job is not None:
        root.after_cancel(timeout_job)
        timeout_job = None
    update_prediction()

canvas.bind("<B1-Motion>", draw_line)
canvas.bind("<ButtonRelease-1>", reset_pos)

# ===============================
# CLEAR BUTTON
# ===============================
def clear_canvas():
    canvas.delete("all")
    draw.rectangle([0, 0, CANVAS_SIZE, CANVAS_SIZE], fill=255)  # Weiß
    update_prediction()


# show the preprocessed image sent to the model
def show_processed():
    proc = preprocess_image(image)
    # enlarge for visibility
    proc_display = proc.resize((IMAGE_SIZE*5, IMAGE_SIZE*5), Image.NEAREST)
    win = tk.Toplevel(root)
    win.title("Processed Input")
    imgtk = ImageTk.PhotoImage(proc_display)
    lbl = tk.Label(win, image=imgtk)
    lbl.image = imgtk
    lbl.pack(padx=10, pady=10)

btn_clear = tk.Button(root, text="Clear", command=clear_canvas)
btn_show = tk.Button(root, text="Show Processed", command=show_processed)
btn_clear.grid(row=1, column=0, pady=5, sticky="w")
btn_show.grid(row=1, column=0, pady=5, sticky="e")

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
def preprocess_image(img_pil):
    """Crop the drawn content and center it in a blank image of size IMAGE_SIZE.

    This helps the network see the character centred even if the user draws
    near the edge of the canvas.
    """
    # convert to numpy array for bounding box detection
    arr = np.array(img_pil)
    # find non-white pixels (ink is black = 0)
    ys, xs = np.where(arr < 255)
    if ys.size == 0:
        # nothing drawn, just resize the whole image
        return img_pil.resize((IMAGE_SIZE, IMAGE_SIZE))

    miny, maxy = ys.min(), ys.max()
    minx, maxx = xs.min(), xs.max()

    # crop the original image to the bounding box
    cropped = img_pil.crop((minx, miny, maxx + 1, maxy + 1))
    # scale it so it fits within IMAGE_SIZE preserving aspect ratio
    # ANTIALIAS was removed in newer Pillow versions; use LANCZOS or fallback
    resample_filter = getattr(Image, "LANCZOS", Image.BICUBIC)
    cropped.thumbnail((IMAGE_SIZE, IMAGE_SIZE), resample_filter)

    # paste onto a white background centered
    new_img = Image.new("L", (IMAGE_SIZE, IMAGE_SIZE), 255)
    paste_x = (IMAGE_SIZE - cropped.width) // 2
    paste_y = (IMAGE_SIZE - cropped.height) // 2
    new_img.paste(cropped, (paste_x, paste_y))
    return new_img


def update_prediction():
    # preprocess and centre the drawing before feeding to the model
    img = preprocess_image(image)
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