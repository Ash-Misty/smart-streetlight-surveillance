
import sys
import subprocess
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

import sounddevice as sd
import soundfile as sf
import numpy as np


# Project paths
BASE_DIR = Path(__file__).resolve().parent
PIPELINE_SCRIPT = BASE_DIR / "pipeline.py"
RECORDINGS_DIR = BASE_DIR / "recordings"

SAMPLE_RATE = 16000
CHANNELS = 1


def record_audio():
    """Record audio from the laptop's selected microphone."""

    print("\n--- Record Audio ---")

    try:
        duration = float(
            input("Enter recording duration in seconds (e.g. 10): ").strip()
        )

        if not 1 <= duration <= 300:
            print("Please enter a duration between 1 and 300 seconds.")
            return None

    except ValueError:
        print("Invalid duration. Enter a number, such as 10.")
        return None

    try:
        print("\nRecording started!")
        print("Speak or play the test sound near your laptop microphone.")
        print("Recording will stop automatically after the selected duration.")

        audio = sd.rec(
            int(duration * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
        )
        sd.wait()

        if audio.size == 0 or np.max(np.abs(audio)) < 1e-5:
            print("No usable audio detected. Check your microphone.")
            return None

        RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

        output_path = RECORDINGS_DIR / "latest_recording.wav"
        sf.write(output_path, audio, SAMPLE_RATE)

        print(f"\nRecording saved to:\n{output_path}")
        return output_path

    except Exception as exc:
        print(f"\nRecording failed: {exc}")
        print("Check microphone permissions and the selected input device.")
        return None


def choose_existing_audio():
    """Open a Windows file picker to select an audio file."""

    root = tk.Tk()
    root.withdraw()

    try:
        root.attributes("-topmost", True)

        selected_file = filedialog.askopenfilename(
            title="Select audio for LumiGuard analysis",
            filetypes=[
                (
                    "Supported audio files",
                    "*.wav *.mp3 *.flac *.ogg *.m4a *.aac",
                ),
                ("All files", "*.*"),
            ],
        )
    finally:
        root.destroy()

    if not selected_file:
        print("No file selected.")
        return None

    path = Path(selected_file)

    if not path.is_file():
        print("The selected file does not exist.")
        return None

    print(f"\nSelected audio:\n{path}")
    return path


def analyze_audio(audio_path):
    """Pass the selected audio to the existing LumiGuard pipeline."""

    if not PIPELINE_SCRIPT.is_file():
        print(f"Cannot find pipeline.py at:\n{PIPELINE_SCRIPT}")
        return

    print("\n" + "=" * 55)
    print("LUMIGUARD AUDIO ANALYSIS")
    print("=" * 55)
    print(f"Input: {audio_path}")
    print("Starting the existing AI pipeline...\n")

    command = [
        sys.executable,
        str(PIPELINE_SCRIPT),
        str(audio_path),
    ]

    try:
        result = subprocess.run(
            command,
            cwd=str(BASE_DIR),
            check=False,
        )

        if result.returncode == 0:
            print("\nLumiGuard analysis finished.")
        else:
            print(
                "\nThe pipeline exited with code "
                f"{result.returncode}. Check the error above."
            )

    except KeyboardInterrupt:
        print("\nAnalysis interrupted.")
    except Exception as exc:
        print(f"Could not start the pipeline: {exc}")


def main():
    if not PIPELINE_SCRIPT.is_file():
        print("Error: pipeline.py was not found in this folder.")
        return

    while True:
        print("\n" + "=" * 45)
        print("       LUMIGUARD - AUDIO ANALYSIS")
        print("=" * 45)
        print("1. Record audio using laptop microphone")
        print("2. Select an existing audio file")
        print("3. Exit")
        print("-" * 45)

        choice = input("Choose an option (1/2/3): ").strip()

        if choice == "1":
            audio_path = record_audio()
        elif choice == "2":
            audio_path = choose_existing_audio()
        elif choice == "3":
            print("Exiting LumiGuard.")
            break
        else:
            print("Invalid choice. Enter 1, 2, or 3.")
            continue

        if audio_path is not None:
            analyze_audio(audio_path)

            input("\nPress Enter to return to the main menu...")


if __name__ == "__main__":
    main()
