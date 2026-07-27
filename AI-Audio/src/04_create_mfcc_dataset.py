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

OUTPUT_PATH = PROJECT_ROOT / "deep_features"

OUTPUT_PATH.mkdir(exist_ok=True)

# -----------------------------

df = pd.read_csv(META_PATH)

X = []

y = []

TARGET_LENGTH = 216

print("=" * 60)
print("Generating MFCC Dataset")
print("=" * 60)

for index, row in df.iterrows():

    file = AUDIO_PATH / row["filename"]

    label = row["category"]

    try:

        audio, sr = librosa.load(file, sr=22050)

        audio, _ = librosa.effects.trim(audio)

        audio = librosa.util.normalize(audio)

        if len(audio) < sr * 5:
            audio = np.pad(audio, (0, sr * 5 - len(audio)))
        else:
            audio = audio[:sr * 5]

        mfcc = librosa.feature.mfcc(
            y=audio,
            sr=sr,
            n_mfcc=40
        )

        # Pad / Trim to 216 frames
        if mfcc.shape[1] < TARGET_LENGTH:
            pad = TARGET_LENGTH - mfcc.shape[1]
            mfcc = np.pad(
                mfcc,
                ((0, 0), (0, pad)),
                mode="constant"
            )
        else:
            mfcc = mfcc[:, :TARGET_LENGTH]

        X.append(mfcc)

        y.append(label)

        if (index + 1) % 100 == 0:
            print(f"Processed {index+1}/2000")

    except Exception as e:
        print(e)

X = np.array(X)

X = X[..., np.newaxis]

encoder = LabelEncoder()

y = encoder.fit_transform(y)

np.save(
    OUTPUT_PATH / "X_cnn.npy",
    X
)

np.save(
    OUTPUT_PATH / "y_cnn.npy",
    y
)

joblib.dump(
    encoder,
    OUTPUT_PATH / "label_encoder.pkl"
)

print()

print("=" * 60)

print("Dataset Ready")

print("=" * 60)

print("Shape :", X.shape)

print("Classes :", len(encoder.classes_))