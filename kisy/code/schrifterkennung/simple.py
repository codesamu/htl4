import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, Flatten, Input, Conv2D, MaxPooling2D, Dropout
from keras.callbacks import EarlyStopping
import numpy as np
import os

# ----------------------------------------------------
# Config
# ----------------------------------------------------
DATA_DIR = "BigDataSet_32x32"   # folder with subfolders A..Z
IMG_SIZE = (32, 32)
BATCH_SIZE = 64
SEED = 123
EPOCHS = 30

# ----------------------------------------------------
# Load data (train / val split)
# ----------------------------------------------------
train_ds = keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2,      # 80/20 split
    subset="training",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    color_mode="grayscale",
)

val_ds = keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2,
    subset="validation",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    color_mode="grayscale",
)

class_names = train_ds.class_names
num_classes = len(class_names)
print("Classes:", class_names)

# ----------------------------------------------------
# Normalization + (optional) data augmentation
# ----------------------------------------------------
normalization_layer = keras.layers.Rescaling(1.0 / 255)

data_augmentation = keras.Sequential(
    [
        keras.layers.RandomRotation(0.05),
        keras.layers.RandomZoom(0.05),
        keras.layers.RandomTranslation(0.05, 0.05),
    ]
)

def preprocess_train(image, label):
    image = normalization_layer(image)
    image = data_augmentation(image)
    return image, label

def preprocess_eval(image, label):
    image = normalization_layer(image)
    return image, label

train_ds = (
    train_ds
    .map(preprocess_train)
    .cache()
    .shuffle(1000)
    .prefetch(buffer_size=tf.data.AUTOTUNE)
)

val_ds = (
    val_ds
    .map(preprocess_eval)
    .cache()
    .prefetch(buffer_size=tf.data.AUTOTUNE)
)

# ----------------------------------------------------
# Define CNN model (similar difficulty as Fashion-MNIST)
# ----------------------------------------------------
model = Sequential(
    [
        Input(shape=(32, 32, 1)),
        Conv2D(32, (3, 3), activation="relu", padding="same"),
        MaxPooling2D(),
        Conv2D(64, (3, 3), activation="relu", padding="same"),
        MaxPooling2D(),
        Conv2D(128, (3, 3), activation="relu", padding="same"),
        MaxPooling2D(),
        Flatten(),
        Dense(256, activation="relu"),
        Dropout(0.4),
        Dense(num_classes, activation="softmax"),
    ]
)

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

model.summary()

# ----------------------------------------------------
# Training with early stopping
# ----------------------------------------------------
early_stop = EarlyStopping(
    monitor="val_accuracy",
    patience=5,
    restore_best_weights=True,
)

history = model.fit(
    train_ds,
    epochs=EPOCHS,
    validation_data=val_ds,
    callbacks=[early_stop],
)

# ----------------------------------------------------
# Evaluate
# ----------------------------------------------------
test_loss, test_acc = model.evaluate(val_ds)
print(f"Validation/Test accuracy: {test_acc:.4f}")

# ----------------------------------------------------
# Save model
# ----------------------------------------------------import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, Flatten, Input, Conv2D, MaxPooling2D, Dropout
from keras.callbacks import EarlyStopping
import os

# --------------------
# Configuration
# --------------------
DATA_DIR = "dataset_32x32"
IMG_SIZE = (32, 32)
BATCH_SIZE = 8        # small batch, more updates from few samples
SEED = 123
EPOCHS = 100          # let early stopping decide

# --------------------
# Load dataset (90% train, 10% test)
# --------------------
train_ds = keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.1,
    subset="training",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    color_mode="grayscale",
)

test_ds = keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.1,
    subset="validation",
    seed=SEED,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    color_mode="grayscale",
)

class_names = train_ds.class_names
num_classes = len(class_names)
print("Classes:", class_names)

# --------------------
# Normalize images
# --------------------
normalization_layer = keras.layers.Rescaling(1.0 / 255)

def preprocess(image, label):
    image = normalization_layer(image)
    return image, label

train_ds = (
    train_ds
    .map(preprocess)
    .cache()
    .shuffle(200)            # small buffer, dataset is tiny
    .prefetch(buffer_size=tf.data.AUTOTUNE)
)

test_ds = (
    test_ds
    .map(preprocess)
    .cache()
    .prefetch(buffer_size=tf.data.AUTOTUNE)
)

# --------------------
# Small CNN model (more like MNIST, but tiny)
# --------------------
model = Sequential(
    [
        Input(shape=(32, 32, 1)),
        Conv2D(16, (3, 3), activation="relu"),
        MaxPooling2D(),
        Conv2D(32, (3, 3), activation="relu"),
        MaxPooling2D(),
        Flatten(),
        Dense(64, activation="relu"),
        Dropout(0.3),
        Dense(num_classes, activation="softmax"),
    ]
)

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

model.summary()

# --------------------
# Train with early stopping on val_loss
# --------------------
early_stop = EarlyStopping(
    monitor="val_loss",
    patience=10,
    restore_best_weights=True,
)

history = model.fit(
    train_ds,
    epochs=EPOCHS,
    validation_data=test_ds,
    callbacks=[early_stop],
)

# --------------------
# Evaluate
# --------------------
test_loss, test_acc = model.evaluate(test_ds)
print(f"Test accuracy: {test_acc:.4f}")

# --------------------
# Save model
# --------------------
os.makedirs("big_models", exist_ok=True)
model.save(os.path.join("big_models", "letter_classifier_small.keras"))
print("Model saved successfully!")

os.makedirs("big_models", exist_ok=True)
model.save(os.path.join("big_models", "letter_classifier_cnn.keras"))
print("Model saved.")
