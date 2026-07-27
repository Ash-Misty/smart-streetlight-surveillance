from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = PROJECT_ROOT / "datasets" / "ESC-50"
META_PATH = DATASET_PATH / "meta" / "esc50.csv"
AUDIO_PATH = DATASET_PATH / "audio"

REPORT_PATH = PROJECT_ROOT / "reports"
REPORT_PATH.mkdir(exist_ok=True)

# --------------------------------------------------
# Load metadata
# --------------------------------------------------

print("=" * 60)
print("Loading ESC-50 metadata...")
print("=" * 60)

df = pd.read_csv(META_PATH)

print(f"Total samples : {len(df)}")
print()

# --------------------------------------------------
# Missing values
# --------------------------------------------------

print("=" * 60)
print("Missing Values")
print("=" * 60)

print(df.isnull().sum())
print()

# --------------------------------------------------
# Duplicate rows
# --------------------------------------------------

duplicates = df.duplicated().sum()

print("=" * 60)
print("Duplicate Rows")
print("=" * 60)
print(duplicates)
print()

# --------------------------------------------------
# Remove duplicates
# --------------------------------------------------

df = df.drop_duplicates().reset_index(drop=True)

# --------------------------------------------------
# Verify audio files
# --------------------------------------------------

print("=" * 60)
print("Checking audio files...")
print("=" * 60)

missing_audio = []

for filename in df["filename"]:
    audio_file = AUDIO_PATH / filename

    if not audio_file.exists():
        missing_audio.append(filename)

print(f"Missing audio files : {len(missing_audio)}")

if missing_audio:
    print(missing_audio[:10])

print()

# --------------------------------------------------
# Dataset statistics
# --------------------------------------------------

print("=" * 60)
print("Dataset Statistics")
print("=" * 60)

print(f"Total classes : {df['category'].nunique()}")
print()

print(df["category"].value_counts())

# --------------------------------------------------
# Human sound categories
# --------------------------------------------------

human_categories = [
    "breathing",
    "clapping",
    "coughing",
    "footsteps",
    "laughing",
    "sneezing",
    "brushing_teeth",
    "drinking_sipping",
    "snoring",
    "crying_baby",
]

df["is_human"] = df["category"].isin(human_categories)

print()
print("=" * 60)
print("Human vs Non-Human")
print("=" * 60)

print(df["is_human"].value_counts())

# --------------------------------------------------
# Save cleaned metadata
# --------------------------------------------------

cleaned_csv = REPORT_PATH / "cleaned_metadata.csv"

df.to_csv(cleaned_csv, index=False)

print()
print("=" * 60)
print("Saved cleaned metadata")
print(cleaned_csv)
print("=" * 60)