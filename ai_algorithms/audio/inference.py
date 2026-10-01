#!/usr/bin/env python3
"""
Vocal Burst Locator - Inference Script

Detects and localizes vocal bursts (laughs, coughs, sneezes, sighs, gasps, cries, etc.)
in audio files. Returns start/end timestamps for each detected event.

Usage:
    python inference.py audio.mp3
    python inference.py audio.wav --threshold 0.7 --device cuda
    python inference.py audio.mp3 --json  # machine-readable output
"""
from __future__ import annotations
import argparse, io, json, sys
from pathlib import Path
from typing import List, Tuple

import numpy as np
import torch
import torch.nn as nn
from transformers import WhisperModel, WhisperFeatureExtractor
from huggingface_hub import hf_hub_download

# ──── Constants ────
SAMPLE_RATE = 16000
CLIP_SECONDS = 30.0
NUM_FRAMES = 1500
REPO_ID = "laion/vocalburst-locator"


# ──── Model ────
class WhisperSegmenter(nn.Module):
    """Whisper-based binary frame segmentation model for vocal burst detection.

    Architecture:
        - Whisper-small encoder (frozen during training, LoRA-adapted)
        - Per-frame projection: Linear(768→384) + GELU + Dropout
        - Temporal convolution: Conv1d(k=7) + GELU + Dropout
        - Output projection: Linear(384→1) → 1 logit per frame

    Output: [batch, 1500] raw logits (50 fps × 30s)
    """

    def __init__(self, whisper_id: str = "openai/whisper-small"):
        super().__init__()
        self.whisper = WhisperModel.from_pretrained(whisper_id)
        d_model = self.whisper.config.d_model  # 768
        hidden = max(256, d_model // 2)        # 384
        self.proj = nn.Sequential(
            nn.Linear(d_model, hidden), nn.GELU(), nn.Dropout(0.1),
        )
        self.temporal = nn.Sequential(
            nn.Conv1d(hidden, hidden, kernel_size=7, padding=3),
            nn.GELU(), nn.Dropout(0.1),
        )
        self.out = nn.Linear(hidden, 1)

    def forward(self, input_features: torch.FloatTensor) -> torch.FloatTensor:
        enc = self.whisper.encoder(input_features=input_features).last_hidden_state
        h = self.proj(enc)               # [B, 1500, 384]
        h = h.permute(0, 2, 1)          # [B, 384, 1500]
        h = self.temporal(h)             # [B, 384, 1500]
        h = h.permute(0, 2, 1)          # [B, 1500, 384]
        logits = self.out(h).squeeze(-1) # [B, 1500]
        return logits


# ──── Post-processing ────
def extract_events(
    probs: np.ndarray,
    threshold: float = 0.65,
    merge_gap: float = 0.3,
    min_dur: float = 0.5,
    clip_seconds: float = CLIP_SECONDS,
    num_frames: int = NUM_FRAMES,
) -> List[Tuple[float, float, float]]:
    """Extract (start_sec, end_sec, confidence) events from frame probabilities.

    Args:
        probs: [num_frames] array of sigmoid probabilities
        threshold: minimum probability to consider a frame as vocal burst
        merge_gap: merge segments closer than this (seconds)
        min_dur: discard segments shorter than this (seconds)

    Returns:
        List of (start_seconds, end_seconds, mean_confidence) tuples
    """
    binary = (probs > threshold).astype(np.float32)
    raw_events = []
    in_event = False
    start = 0
    for f in range(len(binary)):
        if binary[f] > 0.5 and not in_event:
            start = f
            in_event = True
        elif binary[f] <= 0.5 and in_event:
            raw_events.append((start, f))
            in_event = False
    if in_event:
        raw_events.append((start, len(binary)))

    if not raw_events:
        return []

    # Convert to seconds
    frame_to_sec = clip_seconds / num_frames
    events_sec = [(s * frame_to_sec, e * frame_to_sec) for s, e in raw_events]
    frame_ranges = raw_events

    # Merge close segments
    merged = [(events_sec[0], frame_ranges[0])]
    for (s, e), (fs, fe) in zip(events_sec[1:], frame_ranges[1:]):
        prev_s, prev_e = merged[-1][0]
        if s - prev_e <= merge_gap:
            merged[-1] = ((prev_s, e), (merged[-1][1][0], fe))
        else:
            merged.append(((s, e), (fs, fe)))

    # Filter short + compute confidence
    result = []
    for (s, e), (fs, fe) in merged:
        if e - s >= min_dur:
            conf = float(probs[fs:fe].mean())
            result.append((round(s, 3), round(e, 3), round(conf, 3)))

    return result


# ──── Audio loading ────
def load_audio(path: str, target_sr: int = SAMPLE_RATE) -> np.ndarray:
    """Load audio file, convert to mono 16kHz, pad/truncate to 30s."""
    import soundfile as sf
    import librosa

    wav, sr = sf.read(path, dtype="float32", always_2d=False)
    if wav.ndim == 2:
        wav = wav.mean(axis=1)
    if sr != target_sr:
        wav = librosa.resample(wav, orig_sr=sr, target_sr=target_sr)
    clip_samples = int(CLIP_SECONDS * target_sr)
    if len(wav) < clip_samples:
        wav = np.pad(wav, (0, clip_samples - len(wav)))
    else:
        wav = wav[:clip_samples]
    return wav.astype(np.float32)


# ──── Main inference ────
def load_model(device: str = "cpu", checkpoint: str = None) -> Tuple:
    """Load model and feature extractor.

    Args:
        device: "cpu", "cuda", or "cuda:0" etc.
        checkpoint: path to local model.pt, or None to download from HuggingFace

    Returns:
        (model, feature_extractor, device)
    """
    if checkpoint is None:
        checkpoint = hf_hub_download(repo_id=REPO_ID, filename="model.pt")

    dev = torch.device(device)
    model = WhisperSegmenter("openai/whisper-small")
    sd = torch.load(checkpoint, map_location="cpu")
    model.load_state_dict(sd, strict=True)
    model = model.to(dev).eval()

    fe = WhisperFeatureExtractor.from_pretrained("openai/whisper-small")
    return model, fe, dev


def detect_vocal_bursts(
    audio_path: str,
    model=None,
    fe=None,
    device=None,
    threshold: float = 0.65,
    merge_gap: float = 0.3,
    min_dur: float = 0.5,
) -> List[dict]:
    """Detect vocal bursts in an audio file.

    Args:
        audio_path: path to audio file (mp3, wav, flac, etc.)
        model: pre-loaded model (or None to auto-load)
        fe: pre-loaded feature extractor (or None to auto-load)
        device: torch device (or None to auto-detect)
        threshold: detection threshold (0-1, higher = fewer false positives)
        merge_gap: merge events closer than this (seconds)
        min_dur: minimum event duration (seconds)

    Returns:
        List of dicts with keys: start, end, confidence, duration
    """
    if model is None or fe is None:
        dev_str = device if isinstance(device, str) else ("cuda" if torch.cuda.is_available() else "cpu")
        model, fe, device = load_model(dev_str)
    elif device is None:
        device = next(model.parameters()).device

    wav = load_audio(audio_path)
    features = fe(wav, sampling_rate=SAMPLE_RATE, return_tensors="pt")
    x = features.input_features.to(device)

    with torch.no_grad():
        if device.type == "cuda" and torch.cuda.is_bf16_supported():
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = model(x)
        else:
            logits = model(x)
        probs = torch.sigmoid(logits).float().squeeze(0).cpu().numpy()

    events = extract_events(probs, threshold=threshold, merge_gap=merge_gap, min_dur=min_dur)

    return [
        {
            "start": s,
            "end": e,
            "confidence": c,
            "duration": round(e - s, 3),
        }
        for s, e, c in events
    ]


# ──── CLI ────
def main():
    parser = argparse.ArgumentParser(
        description="Detect vocal bursts in audio files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python inference.py recording.mp3
  python inference.py audio.wav --threshold 0.7 --min-dur 0.3
  python inference.py clip.mp3 --json --device cuda
  python inference.py clip.mp3 --checkpoint /path/to/model.pt
        """,
    )
    parser.add_argument("audio", help="Path to audio file (mp3, wav, flac, etc.)")
    parser.add_argument("--threshold", type=float, default=0.65,
                        help="Detection threshold 0-1 (default: 0.65, higher = fewer false positives)")
    parser.add_argument("--merge-gap", type=float, default=0.3,
                        help="Merge events closer than this in seconds (default: 0.3)")
    parser.add_argument("--min-dur", type=float, default=0.5,
                        help="Minimum event duration in seconds (default: 0.5)")
    parser.add_argument("--device", default=None,
                        help="Device: cpu, cuda, cuda:0, etc. (default: auto)")
    parser.add_argument("--checkpoint", default=None,
                        help="Path to model.pt (default: auto-download from HuggingFace)")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON instead of human-readable format")
    args = parser.parse_args()

    if not Path(args.audio).exists():
        print(f"Error: file not found: {args.audio}", file=sys.stderr)
        sys.exit(1)

    dev = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    model, fe, device = load_model(dev, checkpoint=args.checkpoint)

    events = detect_vocal_bursts(
        args.audio, model=model, fe=fe, device=device,
        threshold=args.threshold, merge_gap=args.merge_gap, min_dur=args.min_dur,
    )

    if args.json:
        print(json.dumps({"file": args.audio, "events": events}, indent=2))
    else:
        if not events:
            print(f"No vocal bursts detected in {args.audio}")
        else:
            print(f"Detected {len(events)} vocal burst(s) in {args.audio}:\n")
            for i, ev in enumerate(events, 1):
                print(f"  {i}. {ev['start']:.2f}s - {ev['end']:.2f}s  "
                      f"(duration: {ev['duration']:.2f}s, confidence: {ev['confidence']:.2f})")


if __name__ == "__main__":
    main()
