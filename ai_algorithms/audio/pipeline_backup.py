import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import librosa
import soundfile as sf


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

LOCATOR_SCRIPT = BASE_DIR / "inference.py"

LOCATOR_MODEL = (
    BASE_DIR
    / "models"
    / "vocalburst"
    / "model_v2.pt"
)

CLASSIFIER_SCRIPT = (
    BASE_DIR
    / "models"
    / "vocalburst_classifier"
    / "inference.py"
)


# ============================================================
# RUN VOCALBURST LOCATOR
# ============================================================

def run_locator(audio_file, threshold, merge_gap, min_duration):
    print("\n" + "=" * 70)
    print("STEP 1: VOCALBURST LOCATOR")
    print("=" * 70)

    command = [
        sys.executable,
        str(LOCATOR_SCRIPT),
        str(audio_file),
        "--checkpoint",
        str(LOCATOR_MODEL),
        "--threshold",
        str(threshold),
        "--merge-gap",
        str(merge_gap),
        "--min-dur",
        str(min_duration),
        "--device",
        "cpu",
    ]

    print("\nRunning:")
    print(" ".join(f'"{x}"' if " " in str(x) else str(x) for x in command))
    print()

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("ERROR: VocalBurst Locator failed.")
        print("\nSTDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)

        raise RuntimeError("VocalBurst Locator failed.")

    print(result.stdout)

    # --------------------------------------------------------
    # Parse:
    #
    # 1. 1.28s - 2.32s  (duration: 1.04s, confidence: 0.86)
    # --------------------------------------------------------

    pattern = re.compile(
        r"\s*\d+\.\s*"
        r"(\d+(?:\.\d+)?)s\s*-\s*"
        r"(\d+(?:\.\d+)?)s"
        r"\s*\(duration:\s*"
        r"(\d+(?:\.\d+)?)s,\s*confidence:\s*"
        r"(\d+(?:\.\d+)?)\)"
    )

    bursts = []

    for match in pattern.finditer(result.stdout):
        start = float(match.group(1))
        end = float(match.group(2))
        duration = float(match.group(3))
        confidence = float(match.group(4))

        bursts.append(
            {
                "start": start,
                "end": end,
                "duration": duration,
                "confidence": confidence,
            }
        )

    return bursts


# ============================================================
# EXTRACT DETECTED AUDIO SEGMENT
# ============================================================

def extract_segment(audio_file, start, end, output_file):
    print(
        f"Extracting segment: "
        f"{start:.2f}s → {end:.2f}s"
    )

    audio, sample_rate = librosa.load(
        str(audio_file),
        sr=16000,
        mono=True,
        offset=start,
        duration=end - start,
    )

    sf.write(
        str(output_file),
        audio,
        sample_rate,
    )


# ============================================================
# RUN VOCALBURST CLASSIFIER
# ============================================================

def run_classifier(segment_file, topk):
    print("\n" + "-" * 70)
    print("VOCALBURST CLASSIFIER")
    print("-" * 70)

    command = [
        sys.executable,
        str(CLASSIFIER_SCRIPT),
        str(segment_file),
        "--topk",
        str(topk),
    ]

    print("\nRunning:")
    print(" ".join(f'"{x}"' if " " in str(x) else str(x) for x in command))
    print()

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("ERROR: VocalBurst Classifier failed.")

        print("\nSTDOUT:")
        print(result.stdout)

        print("\nSTDERR:")
        print(result.stderr)

        raise RuntimeError("VocalBurst Classifier failed.")

    print(result.stdout)

    return result.stdout


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description=(
            "LumiGuard Audio Pipeline: "
            "VocalBurst Locator → VocalBurst Classifier"
        )
    )

    parser.add_argument(
        "audio",
        help="Path to input audio file",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.50,
        help="VocalBurst Locator threshold (default: 0.50)",
    )

    parser.add_argument(
        "--merge-gap",
        type=float,
        default=0.10,
        help="Merge nearby bursts within this gap (default: 0.10)",
    )

    parser.add_argument(
        "--min-dur",
        type=float,
        default=0.10,
        help="Minimum burst duration (default: 0.10)",
    )

    parser.add_argument(
        "--topk",
        type=int,
        default=5,
        help="Number of classifier predictions to show (default: 5)",
    )

    args = parser.parse_args()

    audio_file = Path(args.audio).resolve()

    # --------------------------------------------------------
    # CHECK INPUT
    # --------------------------------------------------------

    if not audio_file.exists():
        print(f"\nERROR: Audio file not found:")
        print(audio_file)
        sys.exit(1)

    # --------------------------------------------------------
    # CHECK MODEL FILES
    # --------------------------------------------------------

    if not LOCATOR_SCRIPT.exists():
        print(f"\nERROR: Locator script not found:")
        print(LOCATOR_SCRIPT)
        sys.exit(1)

    if not LOCATOR_MODEL.exists():
        print(f"\nERROR: Locator model not found:")
        print(LOCATOR_MODEL)
        sys.exit(1)

    if not CLASSIFIER_SCRIPT.exists():
        print(f"\nERROR: Classifier script not found:")
        print(CLASSIFIER_SCRIPT)
        sys.exit(1)

    print("\n")
    print("=" * 70)
    print("             LUMIGUARD AUDIO PIPELINE")
    print("=" * 70)

    print(f"\nInput audio:")
    print(audio_file)

    # --------------------------------------------------------
    # STEP 1: LOCATOR
    # --------------------------------------------------------

    bursts = run_locator(
        audio_file,
        args.threshold,
        args.merge_gap,
        args.min_dur,
    )

    # --------------------------------------------------------
    # NO VOCAL BURST
    # --------------------------------------------------------

    if not bursts:
        print("\n" + "=" * 70)
        print("RESULT")
        print("=" * 70)

        print("\nNo vocal bursts detected.")
        print("Classifier was NOT run.")

        print("\nPipeline finished.")
        return

    # --------------------------------------------------------
    # VOCAL BURSTS FOUND
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print(f"DETECTED VOCAL BURSTS: {len(bursts)}")
    print("=" * 70)

    for i, burst in enumerate(bursts, start=1):
        print(
            f"\nBurst {i}: "
            f"{burst['start']:.2f}s → "
            f"{burst['end']:.2f}s | "
            f"duration={burst['duration']:.2f}s | "
            f"locator confidence={burst['confidence']:.2f}"
        )

    # --------------------------------------------------------
    # STEP 2: CLASSIFIER
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("STEP 2: CLASSIFYING DETECTED VOCAL BURSTS")
    print("=" * 70)

    # Temporary directory automatically deleted afterwards
    with tempfile.TemporaryDirectory(
        prefix="lumiguard_vocalburst_"
    ) as temp_dir:

        temp_dir = Path(temp_dir)

        for index, burst in enumerate(bursts, start=1):

            segment_file = (
                temp_dir / f"burst_{index:03d}.wav"
            )

            print("\n")
            print("#" * 70)
            print(f"BURST {index}")
            print("#" * 70)

            # Extract detected part
            extract_segment(
                audio_file,
                burst["start"],
                burst["end"],
                segment_file,
            )

            # Run classifier
            classifier_output = run_classifier(
                segment_file,
                args.topk,
            )

            # ------------------------------------------------
            # DISPLAY PIPELINE RESULT
            # ------------------------------------------------

            print("\n" + "-" * 70)
            print(f"PIPELINE RESULT — BURST {index}")
            print("-" * 70)

            print(
                f"Time: "
                f"{burst['start']:.2f}s → "
                f"{burst['end']:.2f}s"
            )

            print(
                f"Locator confidence: "
                f"{burst['confidence']:.2f}"
            )

            print("\nClassifier output:")
            print(classifier_output)

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)

    print(
        "\nThe original models were NOT modified."
    )


if __name__ == "__main__":
    main()