# from pathlib import Path
# import numpy as np
# import pandas as pd
# import librosa
# import cv2

# # ==========================================================
# # Paths
# # ==========================================================

# PROJECT_ROOT = Path(__file__).resolve().parent.parent

# DATASET_PATH = PROJECT_ROOT / "datasets" / "ESC-50"

# CSV_PATH = DATASET_PATH / "meta" / "esc50.csv"

# AUDIO_PATH = DATASET_PATH / "audio"

# OUTPUT_PATH = PROJECT_ROOT / "mel_features"
# OUTPUT_PATH.mkdir(exist_ok=True)

# # ==========================================================
# # Audio Parameters
# # ==========================================================

# SAMPLE_RATE = 22050

# N_MELS = 128

# N_FFT = 2048

# HOP_LENGTH = 512

# IMG_SIZE = 128

# # ==========================================================
# # Load Metadata
# # ==========================================================

# print("=" * 60)
# print("Generating Log-Mel Spectrogram Dataset")
# print("=" * 60)

# df = pd.read_csv(CSV_PATH)

# X = []

# y = []

# # ==========================================================
# # Process Each Audio File
# # ==========================================================

# for index, row in df.iterrows():

#     file_path = AUDIO_PATH / row["filename"]

#     audio, sr = librosa.load(
#         file_path,
#         sr=SAMPLE_RATE,
#         mono=True
#     )

#     # ------------------------------------------------------
#     # Remove Silence
#     # ------------------------------------------------------

#     audio, _ = librosa.effects.trim(audio)

#     # ------------------------------------------------------
#     # Normalize Audio
#     # ------------------------------------------------------

#     audio = librosa.util.normalize(audio)

#     # ------------------------------------------------------
#     # Log-Mel Spectrogram
#     # ------------------------------------------------------

#     mel = librosa.feature.melspectrogram(
#         y=audio,
#         sr=sr,
#         n_fft=N_FFT,
#         hop_length=HOP_LENGTH,
#         n_mels=N_MELS
#     )

#     log_mel = librosa.power_to_db(
#         mel,
#         ref=np.max
#     )

#     # ------------------------------------------------------
#     # Resize to 128x128
#     # ------------------------------------------------------

#     log_mel = cv2.resize(
#         log_mel,
#         (IMG_SIZE, IMG_SIZE)
#     )

#     # ------------------------------------------------------
#     # Normalize Image
#     # ------------------------------------------------------

#     log_mel = (log_mel - log_mel.min()) / (
#         log_mel.max() - log_mel.min() + 1e-8
#     )

#     log_mel = log_mel.astype(np.float32)

#     log_mel = np.expand_dims(log_mel, axis=-1)

#     X.append(log_mel)

#     y.append(row["target"])

#     if (index + 1) % 100 == 0:

#         print(f"Processed {index+1}/{len(df)}")

# # ==========================================================
# # Convert to NumPy
# # ==========================================================

# X = np.array(X, dtype=np.float32)

# y = np.array(y)

# # ==========================================================
# # Save
# # ==========================================================

# np.save(
#     OUTPUT_PATH / "X_logmel.npy",
#     X
# )

# np.save(
#     OUTPUT_PATH / "y_logmel.npy",
#     y
# )

# print()

# print("=" * 60)
# print("Dataset Successfully Created")
# print("=" * 60)

# print("Shape :", X.shape)

# print("Classes :", len(np.unique(y)))

# print("Saved To :", OUTPUT_PATH)
from pathlib import Path
import numpy as np
import pandas as pd
import librosa
import cv2

# ==========================================================
# Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = PROJECT_ROOT / "datasets" / "ESC-50"

CSV_PATH = DATASET_PATH / "meta" / "esc50.csv"

AUDIO_PATH = DATASET_PATH / "audio"

OUTPUT_PATH = PROJECT_ROOT / "mel_features"
OUTPUT_PATH.mkdir(exist_ok=True)

# ==========================================================
# Parameters
# ==========================================================

SAMPLE_RATE = 22050

N_MELS = 128

N_FFT = 2048

HOP_LENGTH = 512

IMG_SIZE = 128

print("="*60)
print("Creating Augmented Log-Mel Dataset")
print("="*60)

df = pd.read_csv(CSV_PATH)

X = []
y = []

# ==========================================================
# Audio Augmentation Functions
# ==========================================================

def add_noise(audio, noise_factor=0.005):
    noise = np.random.randn(len(audio))
    augmented = audio + noise_factor * noise
    return librosa.util.normalize(augmented)


def pitch_up(audio):
    return librosa.effects.pitch_shift(
        audio,
        sr=SAMPLE_RATE,
        n_steps=2
    )


def pitch_down(audio):
    return librosa.effects.pitch_shift(
        audio,
        sr=SAMPLE_RATE,
        n_steps=-2
    )


def stretch_fast(audio):
    return librosa.effects.time_stretch(
        audio,
        rate=1.1
    )


def stretch_slow(audio):
    return librosa.effects.time_stretch(
        audio,
        rate=0.9
    )


# ==========================================================
# Convert Audio → Log-Mel Spectrogram
# ==========================================================

def create_logmel(audio):

    # Remove silence
    audio, _ = librosa.effects.trim(audio)

    # Normalize
    audio = librosa.util.normalize(audio)

    # Mel Spectrogram
    mel = librosa.feature.melspectrogram(
        y=audio,
        sr=SAMPLE_RATE,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS
    )

    # Convert to log scale
    log_mel = librosa.power_to_db(
        mel,
        ref=np.max
    )

    # Resize to fixed size
    log_mel = cv2.resize(
        log_mel,
        (IMG_SIZE, IMG_SIZE)
    )

    # Normalize to 0-1
    log_mel = (
        log_mel - log_mel.min()
    ) / (
        log_mel.max() - log_mel.min() + 1e-8
    )

    # Add channel dimension
    log_mel = np.expand_dims(
        log_mel.astype(np.float32),
        axis=-1
    )

    return log_mel
# ==========================================================
# Process Dataset
# ==========================================================

print("\nProcessing Audio Files...\n")

for index, row in df.iterrows():

    file_path = AUDIO_PATH / row["filename"]

    audio, sr = librosa.load(
        file_path,
        sr=SAMPLE_RATE,
        mono=True
    )

    # ------------------------------------------------------
    # Original
    # ------------------------------------------------------

    X.append(create_logmel(audio))
    y.append(row["target"])

    # ------------------------------------------------------
    # Pitch Up
    # ------------------------------------------------------

    X.append(create_logmel(
        pitch_up(audio)
    ))
    y.append(row["target"])

    # ------------------------------------------------------
    # Pitch Down
    # ------------------------------------------------------

    X.append(create_logmel(
        pitch_down(audio)
    ))
    y.append(row["target"])

    # ------------------------------------------------------
    # Time Stretch (Fast)
    # ------------------------------------------------------

    X.append(create_logmel(
        stretch_fast(audio)
    ))
    y.append(row["target"])

    # ------------------------------------------------------
    # Time Stretch (Slow)
    # ------------------------------------------------------

    X.append(create_logmel(
        stretch_slow(audio)
    ))
    y.append(row["target"])

    # ------------------------------------------------------
    # Gaussian Noise
    # ------------------------------------------------------

    X.append(create_logmel(
        add_noise(audio)
    ))
    y.append(row["target"])

    if (index + 1) % 50 == 0:

        print(
            f"Processed {index+1}/{len(df)} files"
        )
# ==========================================================
# Convert to NumPy
# ==========================================================

X = np.array(X, dtype=np.float32)
y = np.array(y)

print("\n")
print("=" * 60)
print("Dataset Statistics")
print("=" * 60)

print("Total Samples :", len(X))
print("Number of Classes :", len(np.unique(y)))
print("X Shape :", X.shape)
print("y Shape :", y.shape)

# ==========================================================
# Save Dataset
# ==========================================================

np.save(
    OUTPUT_PATH / "X_logmel.npy",
    X
)

np.save(
    OUTPUT_PATH / "y_logmel.npy",
    y
)

print("\nDataset Saved Successfully")
print("Saved to :", OUTPUT_PATH)