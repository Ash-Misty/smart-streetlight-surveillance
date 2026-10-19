import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
import torch
import torchaudio
import torch.nn as nn
from transformers import AutoModel


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

LOCATOR_SCRIPT = BASE_DIR / "inference.py"
LOCATOR_MODEL = BASE_DIR / "models" / "vocalburst" / "model_v2.pt"
DISTRESS_MODEL = BASE_DIR / "models" / "lumiguard_distress" / "best_model.pt"

SAMPLE_RATE = 16000


# --------------------------------------------------
# LUMIGUARD DISTRESS CLASSIFIER
# Architecture must match the trained checkpoint.
# --------------------------------------------------

class DistressClassifier(nn.Module):
    def __init__(self, input_dim=768):
        super().__init__()

        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.BatchNorm1d(256),
            nn.GELU(),
            nn.Dropout(0.30),
            nn.Linear(256, 128),
            nn.GELU(),
            nn.Dropout(0.20),
            nn.Linear(128, 2),
        )

    def forward(self, x):
        return self.net(x)


class LumiGuardPredictor:
    def __init__(self, device="auto"):
        if device == "auto":
            self.device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )
        else:
            self.device = torch.device(device)

        print(f"\n[INFO] Loading LumiGuard models on {self.device}...")

        if not DISTRESS_MODEL.exists():
            raise FileNotFoundError(
                f"Distress checkpoint not found: {DISTRESS_MODEL}"
            )

        # Load the trained MLP checkpoint.
        checkpoint = torch.load(
            DISTRESS_MODEL,
            map_location="cpu",
            weights_only=False,
        )

        if checkpoint.get("architecture") != "MLP_768_256_128_2":
            raise ValueError(
                "Unexpected checkpoint architecture: "
                f"{checkpoint.get('architecture')}"
            )

        self.classes = checkpoint.get(
            "classes",
            {"normal": 0, "distress": 1},
        )

        self.distress_threshold = float(
            checkpoint.get("distress_threshold", 0.5)
        )

        self.classifier = DistressClassifier(
            input_dim=int(checkpoint.get("input_dim", 768))
        )

        self.classifier.load_state_dict(
            checkpoint["model_state_dict"]
        )
        self.classifier.to(self.device)
        self.classifier.eval()

        # Load the same VoiceCLAP encoder used for training.
        self.voice_encoder = AutoModel.from_pretrained(
            "laion/voiceclap-commercial",
            trust_remote_code=True,
        )
        self.voice_encoder.to(self.device)
        self.voice_encoder.eval()

        print("[INFO] LumiGuard distress classifier loaded.")
        print(
            f"[INFO] Distress decision threshold: "
            f"{self.distress_threshold:.2f}"
        )

    def _make_embedding(self, audio_path):
        # Read audio and convert stereo to mono.
        waveform, sample_rate = sf.read(
            str(audio_path),
            dtype="float32",
        )

        if waveform.ndim == 2:
            waveform = waveform.mean(axis=1)

        if waveform.size == 0:
            raise ValueError("Audio segment is empty.")

        waveform = np.nan_to_num(waveform).astype(np.float32)

        # Resample exactly as required by the training pipeline.
        if sample_rate != SAMPLE_RATE:
            waveform_tensor = torch.from_numpy(waveform)

            waveform_tensor = torchaudio.functional.resample(
                waveform_tensor,
                orig_freq=sample_rate,
                new_freq=SAMPLE_RATE,
            )

            waveform = waveform_tensor.numpy()

        waveform_tensor = torch.from_numpy(
            np.asarray(waveform, dtype=np.float32)
        ).unsqueeze(0).to(self.device)

        with torch.no_grad():
            embedding = self.voice_encoder.encode_waveform(
                waveform_tensor
            )

        if isinstance(embedding, (tuple, list)):
            embedding = embedding[0]

        if isinstance(embedding, dict):
            if "embedding" in embedding:
                embedding = embedding["embedding"]
            else:
                raise ValueError(
                    "VoiceCLAP returned a dictionary without "
                    "an 'embedding' field."
                )

        if not isinstance(embedding, torch.Tensor):
            embedding = torch.as_tensor(embedding)

        embedding = embedding.float().reshape(1, -1)

        if embedding.shape[1] != 768:
            raise ValueError(
                f"Expected 768 embedding values, got "
                f"{embedding.shape[1]}."
            )

        return embedding

    def predict(self, audio_path, threshold=None):
        embedding = self._make_embedding(audio_path)

        with torch.no_grad():
            logits = self.classifier(embedding)
            probabilities = torch.softmax(logits, dim=1)[0]

        normal_id = self.classes["normal"]
        distress_id = self.classes["distress"]

        normal_probability = probabilities[normal_id].item()
        distress_probability = probabilities[distress_id].item()

        decision_threshold = (
            self.distress_threshold
            if threshold is None
            else threshold
        )

        label = (
            "DISTRESS"
            if distress_probability >= decision_threshold
            else "NORMAL"
        )

        return {
            "label": label,
            "normal_probability": normal_probability,
            "distress_probability": distress_probability,
            "threshold": decision_threshold,
        }


# --------------------------------------------------
# VOCAL-BURST LOCATOR
# --------------------------------------------------

def run_locator(
    audio_path,
    threshold=0.50,
    merge_gap=0.10,
    min_duration=0.10,
    device="cpu",
):
    if not LOCATOR_SCRIPT.exists():
        raise FileNotFoundError(
            f"Locator script not found: {LOCATOR_SCRIPT}"
        )

    if not LOCATOR_MODEL.exists():
        raise FileNotFoundError(
            f"Locator checkpoint not found: {LOCATOR_MODEL}"
        )

    command = [
        sys.executable,
        str(LOCATOR_SCRIPT),
        str(audio_path),
        "--checkpoint",
        str(LOCATOR_MODEL),
        "--threshold",
        str(threshold),
        "--merge-gap",
        str(merge_gap),
        "--min-dur",
        str(min_duration),
        "--device",
        device,
    ]

    print("\n[INFO] Locating vocal bursts...")
    print("[INFO] Command:", subprocess.list2cmdline(command))

    result = subprocess.run(
        command,
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True,
        errors="replace",
    )

    if result.stdout:
        print(result.stdout)

    if result.returncode != 0:
        if result.stderr:
            print("[LOCATOR ERROR]")
            print(result.stderr)

        raise RuntimeError(
            f"Vocal-burst locator failed with exit code "
            f"{result.returncode}."
        )

    # Expected locator output:
    # 1. 1.28s - 2.32s (duration: 1.04s, confidence: 0.86)
    pattern = re.compile(
        r"\d+\.\s*"
        r"([\d.]+)s\s*-\s*([\d.]+)s"
        r"\s*\(duration:\s*([\d.]+)s,\s*"
        r"confidence:\s*([\d.]+)\)",
        re.IGNORECASE,
    )

    bursts = []

    for match in pattern.finditer(result.stdout):
        start = float(match.group(1))
        end = float(match.group(2))
        duration = float(match.group(3))
        confidence = float(match.group(4))

        if end > start:
            bursts.append({
                "start": start,
                "end": end,
                "duration": duration,
                "locator_confidence": confidence,
            })

    return bursts


# --------------------------------------------------
# EXTRACT EACH LOCATED SEGMENT
# --------------------------------------------------

def extract_segment(audio_path, start, end, output_path):
    audio, _ = librosa.load(
        str(audio_path),
        sr=SAMPLE_RATE,
        mono=True,
        offset=max(0.0, start),
        duration=max(0.0, end - start),
    )

    if audio.size == 0:
        raise ValueError(
            f"Could not extract audio from {start:.2f}s to {end:.2f}s."
        )

    sf.write(
        str(output_path),
        audio.astype(np.float32),
        SAMPLE_RATE,
    )


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "LumiGuard audio pipeline: vocal-burst locator "
            "followed by the trained distress classifier."
        )
    )

    parser.add_argument(
        "audio",
        help="Path to the input audio file.",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.50,
        help="Vocal-burst locator threshold (default: 0.50).",
    )

    parser.add_argument(
        "--merge-gap",
        type=float,
        default=0.10,
        help="Merge nearby locator detections (default: 0.10).",
    )

    parser.add_argument(
        "--min-dur",
        type=float,
        default=0.10,
        help="Minimum locator event duration (default: 0.10).",
    )

    parser.add_argument(
        "--distress-threshold",
        type=float,
        default=None,
        help=(
            "Distress probability threshold. Defaults to the "
            "value stored in the trained checkpoint (0.50)."
        ),
    )

    parser.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Device for LumiGuard classifier (default: auto).",
    )

    parser.add_argument(
        "--locator-device",
        choices=["cpu", "cuda"],
        default="cpu",
        help="Device for the vocal-burst locator (default: cpu).",
    )

    args = parser.parse_args()

    audio_path = Path(args.audio).resolve()

    if not audio_path.exists():
        raise FileNotFoundError(
            f"Input audio file not found: {audio_path}"
        )

    if args.distress_threshold is not None:
        if not 0.0 <= args.distress_threshold <= 1.0:
            parser.error("--distress-threshold must be between 0 and 1.")

    print("=" * 65)
    print("LUMIGUARD AUDIO DISTRESS DETECTION PIPELINE")
    print("=" * 65)
    print(f"Input audio: {audio_path}")

    # Step 1: Find candidate vocal events.
    bursts = run_locator(
        audio_path=audio_path,
        threshold=args.threshold,
        merge_gap=args.merge_gap,
        min_duration=args.min_dur,
        device=args.locator_device,
    )

    if not bursts:
        print("\n[RESULT] No vocal bursts were detected by the locator.")
        print(
            "[INFO] The distress classifier was not run because "
            "there were no candidate segments."
        )
        return

    print(f"\n[INFO] Candidate vocal bursts: {len(bursts)}")

    # Load VoiceCLAP and the MLP only once.
    predictor = LumiGuardPredictor(device=args.device)

    # Step 2: Classify each candidate segment.
    with tempfile.TemporaryDirectory(prefix="lumiguard_") as temp_dir:
        temp_dir = Path(temp_dir)

        for index, burst in enumerate(bursts, start=1):
            segment_path = temp_dir / f"segment_{index:03d}.wav"

            print("\n" + "-" * 65)
            print(f"EVENT {index}")
            print(
                f"Timestamp: {burst['start']:.2f}s - "
                f"{burst['end']:.2f}s"
            )
            print(f"Duration: {burst['duration']:.2f}s")
            print(
                f"Locator confidence: "
                f"{burst['locator_confidence']:.2%}"
            )

            try:
                extract_segment(
                    audio_path,
                    burst["start"],
                    burst["end"],
                    segment_path,
                )

                prediction = predictor.predict(
                    segment_path,
                    threshold=args.distress_threshold,
                )

                print(
                    f"Normal probability: "
                    f"{prediction['normal_probability']:.2%}"
                )
                print(
                    f"Distress probability: "
                    f"{prediction['distress_probability']:.2%}"
                )
                print(
                    f"Classifier threshold: "
                    f"{prediction['threshold']:.2f}"
                )

                if prediction["label"] == "DISTRESS":
                    print(
                        "[RESULT] POTENTIAL DISTRESS DETECTED"
                    )
                else:
                    print("[RESULT] Classified as NORMAL")

            except Exception as exc:
                print(
                    f"[ERROR] Could not classify event {index}: {exc}"
                )

    print("\n" + "=" * 65)
    print("PIPELINE FINISHED")
    print("=" * 65)
    print(
        "Note: A distress classification is a potential-distress "
        "signal, not proof that a crime occurred."
    )


if __name__ == "__main__":
    main()
