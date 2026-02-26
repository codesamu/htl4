# Handwritten Letter Recognition System (A-Z)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)
![Keras](https://img.shields.io/badge/Keras-2.x-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

A deep learning system for recognizing handwritten letters (A-Z) using Convolutional Neural Networks (CNN). This project consists of two main components: a model training script and an interactive drawing application for real-time letter recognition.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
  - [Model Training (`model.py`)](#model-training-modelpy)
  - [Interactive Drawing App (`big-set-draw.py`)](#interactive-drawing-app-big-set-drawpy)
- [Installation](#installation)
- [Usage](#usage)
- [Model Architecture](#model-architecture)
- [Dataset](#dataset)
- [Performance](#performance)

---

## 🎯 Overview

This project implements a complete handwritten letter recognition pipeline:

1. **Training**: Train a CNN model on a dataset of handwritten letters (A-Z)
2. **Recognition**: Use the trained model to recognize letters drawn in real-time through a GUI application

The system uses a Convolutional Neural Network architecture optimized for 32x32 grayscale images.

---

## ✨ Features

- 🎨 **Interactive Drawing Canvas**: Draw letters with your mouse/touchpad
- ⚡ **Real-time Recognition**: Instant predictions as you draw
- 📊 **Visual Feedback**: Live probability bar chart for all 26 letters
- 🧠 **Deep Learning**: CNN-based model with high accuracy
- 🎯 **26 Classes**: Recognizes all uppercase letters A-Z
- 💾 **Model Persistence**: Save and load trained models

---

## 📦 Requirements

```
Python 3.8+
TensorFlow 2.x
Keras 2.x
NumPy
OpenCV (cv2)
Pillow (PIL)
Matplotlib
scikit-learn
tkinter (usually included with Python)
```

---

## 📁 Project Structure

```
.
├── model.py              # Model training script
├── draw.py       # Interactive drawing application
├── handschrift_A_Z_model.h5  # Trained model (generated)
├── BigDataSet_32x32/     # Training dataset folder
│   ├── A/                # Letter A samples
│   ├── B/                # Letter B samples
│   └── ...               # Letters C-Z
├── README.md             # This file
```
├── better-draw.py        # Interactive drawing GUI with centering

---

## 🔧 How It Works

### Model Training (`model.py`)

The training script builds and trains a CNN model for letter recognition.

#### **Data Loading**
```python
def load_data():
    # Loads images from BigDataSet_32x32 folder
    # Each subfolder (A-Z) contains training samples
    # Images are resized to 32x32 pixels
```

**Process:**
1. Scans `BigDataSet_32x32` directory for letter folders (A-Z)
2. Loads images using OpenCV in grayscale mode
3. Resizes all images to 32×32 pixels
4. Converts to NumPy arrays and normalizes pixel values (0-255 → 0-1)
5. Creates labels (0-25) corresponding to letters A-Z

#### **Model Architecture**
```
Input (32×32×1 grayscale)
    ↓
Conv2D(32 filters, 3×3) + ReLU
    ↓
MaxPooling2D(2×2)
    ↓
Conv2D(64 filters, 3×3) + ReLU
    ↓
MaxPooling2D(2×2)
    ↓
Flatten
    ↓
Dense(128) + ReLU
    ↓
Dense(26) + Softmax → Output (A-Z probabilities)
```

#### **Training Process**
1. **Data Preprocessing**: Normalizes pixel values to [0, 1] range
2. **Train/Test Split**: 90% training, 10% testing
3. **Model Compilation**: 
   - Optimizer: Adam
   - Loss: Sparse Categorical Crossentropy
   - Metric: Accuracy
4. **Training**: Trains for 10 epochs with batch size 32
5. **Evaluation**: Tests on held-out test set
6. **Saving**: Saves model as `handschrift_A_Z_model.h5`

**Key Parameters:**
- `IMAGE_SIZE = 32`: Input image dimensions
- `EPOCHS = 10`: Number of training epochs
- `BATCH_SIZE = 32`: Batch size for training
- `MAX_IMAGES_PER_LETTER = 8000`: Limit on training samples per letter

---

### Interactive Drawing App (`big-set-draw.py`)

A real-time letter recognition GUI application built with Tkinter.

#### **Components**

1. **Drawing Canvas** (320×320 pixels)
   - White background for drawing
   - Mouse/touch input tracking
   - Smooth line drawing with rounded caps

2. **Real-time Prediction Engine**
   - Captures drawing on PIL Image object
   - Resizes to 32×32 pixels (matching model input)
   - Normalizes pixel values
   - Feeds to trained model for prediction

3. **Visual Feedback**
   - **Bar Chart**: Shows probability distribution for all 26 letters
   - **Top Prediction**: Displays the most likely letter with confidence
   - Updates in real-time as you draw

#### **Workflow**

```
User draws on canvas
    ↓
Mouse events captured → PIL Image updated
    ↓
Image resized to 32×32
    ↓
Normalized to [0, 1] range
    ↓
Reshaped to (1, 32, 32, 1) batch format
    ↓
Model prediction → 26 probabilities
    ↓
Bar chart updated + Top prediction shown
```

#### **Key Functions**

- **`draw_line(event)`**: Captures mouse movement and draws lines
- **`update_prediction()`**: Processes image and updates predictions
- **`clear_canvas()`**: Resets the drawing area

**Parameters:**
- `CANVAS_SIZE = 320`: Drawing canvas size (pixels)
- `IMAGE_SIZE = 32`: Model input size (pixels)
- `MODEL_PATH = "handschrift_A_Z_model.h5"`: Path to trained model

---

## 🚀 Installation

1. **Clone or download this repository**

2. **Install dependencies:**
```bash
pip install tensorflow keras numpy opencv-python pillow matplotlib scikit-learn
```

3. **Prepare dataset:**
   - Ensure `BigDataSet_32x32` folder exists
   - Folder should contain subfolders A-Z, each with training images

---

## 💻 Usage

### Training the Model

```bash
python model.py
```

This will:
- Load data from `BigDataSet_32x32/`
- Train the CNN model
- Save the model as `handschrift_A_Z_model.h5`
- Display training accuracy and test results

### Running the Drawing App

```bash
python big-set-draw.py
```

**How to use:**
1. Launch the application
2. Draw a letter (A-Z) on the white canvas using your mouse
3. Watch the real-time predictions update as you draw
4. The bar chart shows confidence scores for all letters
5. Click "Clear" to start over

**Tips for best results:**
- Draw large, clear letters
- Fill the canvas area
- Use consistent stroke width
- Draw uppercase letters

---

## 🏗️ Model Architecture

The CNN model uses a classic architecture pattern:

| Layer | Type | Parameters | Output Shape |
|-------|------|------------|--------------|
| Input | - | - | (32, 32, 1) |
| Conv1 | Conv2D | 32 filters, 3×3 | (30, 30, 32) |
| Pool1 | MaxPooling2D | 2×2 | (15, 15, 32) |
| Conv2 | Conv2D | 64 filters, 3×3 | (13, 13, 64) |
| Pool2 | MaxPooling2D | 2×2 | (6, 6, 64) |
| Flatten | - | - | (2304,) |
| Dense1 | Dense | 128 units | (128,) |
| Output | Dense | 26 units + Softmax | (26,) |

**Total Parameters:** ~300K trainable parameters

---

## 📊 Dataset

The model is trained on the `BigDataSet_32x32` dataset:
- **Format**: 32×32 grayscale images
- **Classes**: 26 (A-Z)
- **Structure**: One folder per letter containing training samples
- **Preprocessing**: Images are normalized to [0, 1] range

---

## 📈 Performance

- **Training Accuracy**: Typically achieves 85-95% accuracy
- **Test Accuracy**: Validated on held-out test set
- **Inference Speed**: Real-time predictions (<100ms per frame)
- **Model Size**: ~1-2 MB (`.h5` format)

---

## 🎓 Technical Details

### Image Preprocessing Pipeline

**Training:**
```
Raw Image (any size) 
  → Resize to 32×32 
  → Grayscale conversion 
  → Normalize [0, 255] → [0, 1]
  → Reshape to (32, 32, 1)
```

**Inference:**
```
Canvas Drawing (320×320)
  → Resize to 32×32 (LANCZOS)
  → Convert to NumPy array
  → Normalize [0, 255] → [0, 1]
  → Reshape to (1, 32, 32, 1) batch
```

### Model Output

The model outputs a probability distribution over 26 classes:
- Each output value represents confidence for one letter (A-Z)
- Values sum to 1.0 (softmax activation)
- Highest probability indicates predicted letter

---

## 🔍 Troubleshooting

**Model not found error:**
- Ensure `handschrift_A_Z_model.h5` exists in the same directory
- Train the model first using `model.py`

**Poor recognition accuracy:**
- Draw larger, clearer letters
- Ensure consistent stroke width
- Try drawing in the center of the canvas

**Import errors:**
- Install missing dependencies: `pip install [package-name]`
- Check Python version (3.8+ required)

---

## 🙏 Acknowledgments

- TensorFlow/Keras for deep learning framework
- OpenCV for image processing
- Tkinter for GUI development
- Matplotlib for visualization

---

