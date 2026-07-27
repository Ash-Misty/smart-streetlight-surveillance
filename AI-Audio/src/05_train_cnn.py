from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D,
    MaxPooling2D,
    BatchNormalization,
    Dropout,
    Flatten,
    Dense
)

from tensorflow.keras.callbacks import (
    EarlyStopping,
    ReduceLROnPlateau,
    ModelCheckpoint
)

# ----------------------------------------------------
# Paths
# ----------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = PROJECT_ROOT / "deep_features"

MODEL_PATH = PROJECT_ROOT / "models"
MODEL_PATH.mkdir(exist_ok=True)

PLOT_PATH = PROJECT_ROOT / "plots"
PLOT_PATH.mkdir(exist_ok=True)

# ----------------------------------------------------
# Load Dataset
# ----------------------------------------------------

X = np.load(DATA_PATH / "X_cnn.npy")
y = np.load(DATA_PATH / "y_cnn.npy")

print("Dataset Loaded")

print("X Shape :", X.shape)
print("y Shape :", y.shape)

# ----------------------------------------------------
# Split
# ----------------------------------------------------

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.5,
    random_state=42,
    stratify=y_temp
)

print()

print("Training :", X_train.shape)
print("Validation :", X_val.shape)
print("Testing :", X_test.shape)

# ----------------------------------------------------
# CNN
# ----------------------------------------------------

model = Sequential([

    Conv2D(
        32,
        (3,3),
        activation="relu",
        input_shape=(40,216,1)
    ),

    BatchNormalization(),

    MaxPooling2D(),

    Dropout(0.25),

    Conv2D(
        64,
        (3,3),
        activation="relu"
    ),

    BatchNormalization(),

    MaxPooling2D(),

    Dropout(0.25),

    Conv2D(
        128,
        (3,3),
        activation="relu"
    ),

    BatchNormalization(),

    MaxPooling2D(),

    Dropout(0.3),

    Flatten(),

    Dense(
        256,
        activation="relu"
    ),

    Dropout(0.4),

    Dense(
        50,
        activation="softmax"
    )

])

model.summary()

# ----------------------------------------------------
# Compile
# ----------------------------------------------------

model.compile(

    optimizer="adam",

    loss="sparse_categorical_crossentropy",

    metrics=["accuracy"]

)

# ----------------------------------------------------
# Callbacks
# ----------------------------------------------------

callbacks = [

    EarlyStopping(
        patience=10,
        restore_best_weights=True
    ),

    ReduceLROnPlateau(
        patience=5,
        factor=0.5
    ),

    ModelCheckpoint(
        MODEL_PATH / "best_model.keras",
        save_best_only=True
    )

]

# ----------------------------------------------------
# Train
# ----------------------------------------------------

history = model.fit(

    X_train,
    y_train,

    validation_data=(X_val,y_val),

    epochs=50,

    batch_size=32,

    callbacks=callbacks

)

# ----------------------------------------------------
# Evaluate
# ----------------------------------------------------

loss, accuracy = model.evaluate(
    X_test,
    y_test
)

print()

print("Test Accuracy :", accuracy)

# ----------------------------------------------------
# Save Final Model
# ----------------------------------------------------

model.save(
    MODEL_PATH / "final_model.keras"
)

# ----------------------------------------------------
# Accuracy Graph
# ----------------------------------------------------

plt.figure(figsize=(8,5))

plt.plot(history.history["accuracy"],label="Train")

plt.plot(history.history["val_accuracy"],label="Validation")

plt.legend()

plt.xlabel("Epoch")

plt.ylabel("Accuracy")

plt.title("Training Accuracy")

plt.savefig(PLOT_PATH/"accuracy.png")

plt.close()

# ----------------------------------------------------
# Loss Graph
# ----------------------------------------------------

plt.figure(figsize=(8,5))

plt.plot(history.history["loss"],label="Train")

plt.plot(history.history["val_loss"],label="Validation")

plt.legend()

plt.xlabel("Epoch")

plt.ylabel("Loss")

plt.title("Training Loss")

plt.savefig(PLOT_PATH/"loss.png")

plt.close()

print()

print("="*60)

print("Training Completed")

print("="*60)