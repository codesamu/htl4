import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import numpy as np
from PIL import Image, ImageTk
import tensorflow as tf
from tensorflow import keras

# -------------------------
# CONFIG
# -------------------------
MODEL_PATH = "big_models/letter_classifier_small.keras"  # adjust if needed
IMG_SIZE = (32, 32)                                  # must match your training
CLASS_NAMES = [chr(ord("A") + i) for i in range(26)] # A..Z

# -------------------------
# LOAD MODEL
# -------------------------
model = keras.models.load_model(MODEL_PATH)

# -------------------------
# IMAGE PREPROCESSING
# -------------------------
def preprocess_image(path):
    img = Image.open(path).convert("L")        # grayscale
    img = img.resize(IMG_SIZE)
    img_arr = np.array(img).astype("float32") / 255.0
    img_arr = np.expand_dims(img_arr, axis=-1) # (32, 32, 1)
    img_arr = np.expand_dims(img_arr, axis=0)  # (1, 32, 32, 1)
    return img_arr, img

# -------------------------
# GUI APP
# -------------------------
class LetterClassifierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Letter Classifier")

        # Frame for image
        self.image_label = tk.Label(self.root, text="No image loaded")
        self.image_label.pack(padx=10, pady=10)

        # Button to open file
        self.open_button = tk.Button(
            self.root,
            text="Select Image",
            command=self.load_and_predict_image
        )
        self.open_button.pack(padx=10, pady=5)

        # Frame for predictions
        self.pred_frame = tk.Frame(self.root)
        self.pred_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Treeview to show probabilities
        self.tree = ttk.Treeview(
            self.pred_frame,
            columns=("Letter", "Probability"),
            show="headings",
            height=10
        )
        self.tree.heading("Letter", text="Letter")
        self.tree.heading("Probability", text="Probability")
        self.tree.column("Letter", width=80, anchor=tk.CENTER)
        self.tree.column("Probability", width=120, anchor=tk.CENTER)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(
            self.pred_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Label for top prediction
        self.top_pred_label = tk.Label(self.root, text="", font=("Helvetica", 14))
        self.top_pred_label.pack(padx=10, pady=10)

        # Keep reference to PhotoImage
        self._photo = None

    def load_and_predict_image(self):
        file_path = filedialog.askopenfilename(
            title="Select letter image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if not file_path:
            return

        # Preprocess for model
        x, pil_img = preprocess_image(file_path)

        # Show image (scaled up for visibility)
        display_img = pil_img.resize((128, 128), Image.NEAREST)
        self._photo = ImageTk.PhotoImage(display_img)
        self.image_label.configure(image=self._photo, text="")

        # Predict
        probs = model.predict(x)[0]  # shape: (num_classes,)

        # Clear tree and fill with new data (sorted by prob desc)
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Pair class names with probabilities
        items = list(zip(CLASS_NAMES, probs))
        items.sort(key=lambda t: t[1], reverse=True)

        for letter, p in items:
            self.tree.insert("", tk.END, values=(letter, f"{p*100:.2f} %"))

        # Top prediction
        best_letter, best_prob = items[0]
        self.top_pred_label.configure(
            text=f"Top prediction: {best_letter} ({best_prob*100:.2f} %)"
        )

# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = LetterClassifierGUI(root)
    root.mainloop()
