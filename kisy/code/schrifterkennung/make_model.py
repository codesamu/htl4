import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

# PARAMETER
IMAGE_SIZE = 32
MAX_IMAGES_PER_LETTER = 8000
EPOCHS = 10
BATCH_SIZE = 32

# DATEN LADEN
def load_data():
    features = []
    labels = []

    base_dir = r"BigDataSet_32x32"

    folders = sorted([
        f for f in os.listdir(base_dir)
        if len(f) == 1 and os.path.isdir(os.path.join(base_dir, f))
    ])

    if not folders:
        raise Exception("Keine Buchstabenordner (A–Z) gefunden!")

    for label, folder in enumerate(folders):
        folder_path = os.path.join(base_dir, folder)
        files = os.listdir(folder_path)

        for file in files:
            image_path = os.path.join(folder_path, file)
            image = cv2.imread(image_path, 0)

            if image is None:
                continue

            image = cv2.resize(image, (IMAGE_SIZE, IMAGE_SIZE))
            features.append(image)
            labels.append(label)

    X = np.array(features, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)

    print("Geladene Daten:", X.shape)
    return X, y


def main():
    X, y = load_data()

    # Normalisieren
    X = X / 255.0
    X = X.reshape(-1, IMAGE_SIZE, IMAGE_SIZE, 1)

    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.1, shuffle=True, random_state=42
    )

    # CNN-Modell
    model = Sequential()
    model.add(Conv2D(32, (3,3), activation='relu', input_shape=(IMAGE_SIZE,IMAGE_SIZE,1)))
    model.add(MaxPooling2D((2,2)))

    model.add(Conv2D(64, (3,3), activation='relu'))
    model.add(MaxPooling2D((2,2)))

    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dense(26, activation='softmax'))

    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    model.summary()

    # Training
    history = model.fit(
        X_train,
        y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=0.1
    )

    # Testen
    loss, acc = model.evaluate(X_test, y_test)
    print("Test Accuracy:", acc)

    # Modell speichern
    model.save("handschrift_A_Z_model.h5")
    print("Modell gespeichert als handschrift_A_Z_model.h5")


# ===============================
# START
# ===============================
if __name__ == "__main__":
    main()