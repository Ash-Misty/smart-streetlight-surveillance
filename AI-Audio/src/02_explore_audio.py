from pathlib import Path
import librosa
import librosa.display
import matplotlib.pyplot as plt
import soundfile as sf
import pandas as pd
import numpy as np

# -------------------------------------------------
# Paths
# -------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = PROJECT_ROOT / "datasets" / "ESC-50"

META_PATH = DATASET_PATH / "meta" / "esc50.csv"

AUDIO_PATH = DATASET_PATH / "audio"

PLOT_PATH = PROJECT_ROOT / "plots"
PLOT_PATH.mkdir(exist_ok=True)

OUTPUT_PATH = PROJECT_ROOT / "processed_audio"
OUTPUT_PATH.mkdir(exist_ok=True)

# -------------------------------------------------
# Load metadata
# -------------------------------------------------

df = pd.read_csv(META_PATH)

print("=" * 60)
print("Dataset Loaded")
print("=" * 60)

# -------------------------------------------------
# Select one audio
# -------------------------------------------------

sample = df.iloc[0]

filename = sample["filename"]

category = sample["category"]

audio_file = AUDIO_PATH / filename

print(f"Category : {category}")
print(f"Filename : {filename}")

# -------------------------------------------------
# Load audio
# -------------------------------------------------

audio, sr = librosa.load(audio_file, sr=22050)

print(f"Sample Rate : {sr}")
print(f"Samples : {len(audio)}")

duration = librosa.get_duration(y=audio, sr=sr)

print(f"Duration : {duration:.2f} seconds")

# -------------------------------------------------
# Waveform
# -------------------------------------------------

plt.figure(figsize=(12,4))

librosa.display.waveshow(audio, sr=sr)

plt.title("Waveform")

plt.tight_layout()

plt.savefig(PLOT_PATH/"waveform.png")

plt.close()

print("Waveform saved")

# -------------------------------------------------
# Trim Silence
# -------------------------------------------------

trimmed_audio, index = librosa.effects.trim(audio)

print(f"Original Samples : {len(audio)}")
print(f"Trimmed Samples : {len(trimmed_audio)}")

# -------------------------------------------------
# Normalize
# -------------------------------------------------

normalized_audio = librosa.util.normalize(trimmed_audio)

# -------------------------------------------------
# Save Processed Audio
# -------------------------------------------------

sf.write(
    OUTPUT_PATH/"processed_audio.wav",
    normalized_audio,
    sr
)

print("Processed audio saved")

# -------------------------------------------------
# Mel Spectrogram
# -------------------------------------------------

mel = librosa.feature.melspectrogram(
    y=normalized_audio,
    sr=sr
)

mel_db = librosa.power_to_db(mel)

plt.figure(figsize=(12,5))

librosa.display.specshow(
    mel_db,
    sr=sr,
    x_axis="time",
    y_axis="mel"
)

plt.colorbar()

plt.title("Mel Spectrogram")

plt.tight_layout()

plt.savefig(PLOT_PATH/"mel_spectrogram.png")

plt.close()

print("Mel Spectrogram saved")

# -------------------------------------------------
# MFCC
# -------------------------------------------------

mfcc = librosa.feature.mfcc(
    y=normalized_audio,
    sr=sr,
    n_mfcc=40
)

plt.figure(figsize=(12,5))

librosa.display.specshow(
    mfcc,
    x_axis="time"
)

plt.colorbar()

plt.title("MFCC")

plt.tight_layout()

plt.savefig(PLOT_PATH/"mfcc.png")

plt.close()

print("MFCC saved")

print("=" * 60)
print("Module 2 Completed Successfully")
print("=" * 60)