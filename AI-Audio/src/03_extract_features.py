from pathlib import Path
import librosa
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib

# -----------------------------
# Paths
# -----------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = PROJECT_ROOT / "datasets" / "ESC-50"
META_PATH = DATASET_PATH / "meta" / "esc50.csv"
AUDIO_PATH = DATASET_PATH / "audio"

FEATURE_PATH = PROJECT_ROOT / "features"
FEATURE_PATH.mkdir(exist_ok=True)

# -----------------------------
# Load Metadata
# -----------------------------

df = pd.read_csv(META_PATH)

print("=" * 60)
print("Extracting Features...")
print("=" * 60)

X = []
y = []

# -----------------------------
# Feature Extraction
# -----------------------------

for index, row in df.iterrows():

    filename = row["filename"]
    category = row["category"]

    file_path = AUDIO_PATH / filename

    try:

        # Load Audio
        audio, sr = librosa.load(file_path, sr=22050)

        # Remove Silence
        audio, _ = librosa.effects.trim(audio)

        # Normalize
        audio = librosa.util.normalize(audio)

        # Fix Length (5 seconds)
        target_length = sr * 5

        if len(audio) < target_length:
            audio = np.pad(audio, (0, target_length - len(audio)))
        else:
            audio = audio[:target_length]

        # MFCC
        mfcc = librosa.feature.mfcc(
            y=audio,
            sr=sr,
            n_mfcc=40
        )

        # Average across time
        mfcc = np.mean(mfcc.T, axis=0)

        X.append(mfcc)
        y.append(category)

        if (index + 1) % 100 == 0:
            print(f"Processed {index+1}/2000")

    except Exception as e:
        print(f"Skipped {filename}: {e}")

# -----------------------------
# Convert to NumPy
# -----------------------------

X = np.array(X)

# -----------------------------
# Encode Labels
# -----------------------------

encoder = LabelEncoder()

y_encoded = encoder.fit_transform(y)

# -----------------------------
# Save Everything
# -----------------------------

np.save(FEATURE_PATH / "X.npy", X)
np.save(FEATURE_PATH / "y.npy", y_encoded)

joblib.dump(
    encoder,
    FEATURE_PATH / "label_encoder.pkl"
)

df[["filename", "category"]].to_csv(
    FEATURE_PATH / "labels.csv",
    index=False
)

print()

print("=" * 60)
print("Feature Extraction Completed")
print("=" * 60)

print(f"Samples : {X.shape[0]}")
print(f"Features : {X.shape[1]}")
print(f"Classes : {len(encoder.classes_)}")