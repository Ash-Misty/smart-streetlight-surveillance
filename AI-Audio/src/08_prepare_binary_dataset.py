from pathlib import Path

import librosa
import numpy as np
import pandas as pd
import tensorflow as tf

# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = PROJECT_ROOT / "models" / "best_logmel_model.keras"

META_PATH = (
    PROJECT_ROOT
    / "datasets"
    / "ESC-50"
    / "meta"
    / "esc50.csv"
)

TEST_AUDIO = (
    PROJECT_ROOT
    / "test_audio"
    / "samp2.mp3"
)

# ============================================================
# Load Model
# ============================================================

print("="*60)
print("Loading CNN Model")
print("="*60)

model = tf.keras.models.load_model(MODEL_PATH)

print("Model Loaded Successfully")

# ============================================================
# Load Labels
# ============================================================

df = pd.read_csv(META_PATH)

labels = sorted(df["category"].unique())

print("\nTotal Classes :", len(labels))

# ============================================================
# Human Classes
# ============================================================

HUMAN_CLASSES = {

    "breathing",
    "clapping",
    "coughing",
    "drinking_sipping",
    "footsteps",
    "laughing",
    "sneezing",
    "brushing_teeth",
    "keyboard_typing"

}

# ============================================================
# Feature Extraction
# ============================================================

def extract_logmel(file):

    signal, sr = librosa.load(
        file,
        sr=22050
    )

    mel = librosa.feature.melspectrogram(
        y=signal,
        sr=sr,
        n_mels=128
    )

    mel = librosa.power_to_db(
        mel,
        ref=np.max
    )

    mel = librosa.util.fix_length(
        mel,
        size=128,
        axis=1
    )

    mel = mel.reshape(128,128,1)

    mel = mel.astype(np.float32)

    mel = np.expand_dims(mel,axis=0)

    return mel

# ============================================================
# Prediction
# ============================================================

print("\nProcessing Audio...")

X = extract_logmel(TEST_AUDIO)

prediction = model.predict(X,verbose=0)

index = np.argmax(prediction)

confidence = prediction[0][index]

label = labels[index]

# ============================================================
# Result
# ============================================================

print("\n"+"="*60)
print("Prediction Result")
print("="*60)

print("Predicted Sound :",label)

print("Confidence : {:.2f}%".format(confidence*100))

if label in HUMAN_CLASSES:

    print("\nHuman Sound Detected")

    print("Human Activity :",label)

else:

    print("\nNon-Human Sound Detected")

    print("Category :",label)

print("="*60)