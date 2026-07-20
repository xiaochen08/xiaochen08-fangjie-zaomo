#!/usr/bin/env python3
"""Inspect source audio and create versioned Minecraft OGG copies without touching originals."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import struct
import subprocess
import sys
import wave
from pathlib import Path
from typing import Any, Iterable


class AudioToolError(RuntimeError):
    """Raised for safe, user-actionable audio pipeline failures."""


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _decode_pcm(raw: bytes, sample_width: int) -> list[int]:
    if sample_width == 1:
        return [value - 128 for value in raw]
    if sample_width == 2:
        count = len(raw) // 2
        return list(struct.unpack(f"<{count}h", raw))
    if sample_width == 3:
        values = []
        for offset in range(0, len(raw), 3):
            chunk = raw[offset : offset + 3]
            unsigned = int.from_bytes(chunk, "little", signed=False)
            values.append(unsigned - (1 << 24) if unsigned & (1 << 23) else unsigned)
        return values
    if sample_width == 4:
        count = len(raw) // 4
        return list(struct.unpack(f"<{count}i", raw))
    raise AudioToolError(f"Unsupported PCM sample width: {sample_width} bytes")


def _dbfs(value: float, full_scale: float) -> float | None:
    if value <= 0:
        return None
    return round(20.0 * math.log10(value / full_scale), 3)


def _inspect_wav(path: Path) -> dict[str, Any]:
    try:
        with wave.open(str(path), "rb") as wav:
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            sample_rate = wav.getframerate()
            frame_count = wav.getnframes()
            compression = wav.getcomptype()
            raw = wav.readframes(frame_count)
    except (wave.Error, EOFError) as exc:
        raise AudioToolError(f"Invalid WAV file: {path}: {exc}") from exc

    if compression != "NONE":
        raise AudioToolError(f"Compressed WAV is not supported without FFmpeg: {path}")
    if channels < 1 or sample_rate < 1:
        raise AudioToolError(f"Invalid WAV metadata: {path}")

    samples = _decode_pcm(raw, sample_width)
    full_scale = float(1 << (sample_width * 8 - 1))
    peak = max((abs(value) for value in samples), default=0)
    rms = math.sqrt(sum(value * value for value in samples) / len(samples)) if samples else 0.0
    threshold = full_scale * 10 ** (-60 / 20)

    frame_peaks = [
        max(abs(value) for value in samples[index : index + channels])
        for index in range(0, len(samples), channels)
    ]
    first_active = next((i for i, value in enumerate(frame_peaks) if value > threshold), len(frame_peaks))
    last_active = next(
        (i for i, value in enumerate(reversed(frame_peaks)) if value > threshold),
        len(frame_peaks),
    )

    return {
        "format": "wav",
        "duration_seconds": round(frame_count / sample_rate, 6),
        "channels": channels,
        "sample_rate_hz": sample_rate,
        "sample_width_bits": sample_width * 8,
        "peak_dbfs": _dbfs(float(peak), full_scale),
        "rms_dbfs": _dbfs(rms, full_scale),
        "leading_silence_ms": round(first_active * 1000 / sample_rate, 3),
        "trailing_silence_ms": round(last_active * 1000 / sample_rate, 3),
    }


def resolve_tool(name: str) -> str:
    resolved = shutil.which(name)
    if not resolved:
        raise AudioToolError(
            f"Required audio tool '{name}' was not found. Install it yourself or provide WAV for inspection; the Skill will not install system software."
        )
    return resolved


def _inspect_with_ffprobe(path: Path) -> dict[str, Any]:
    ffprobe = resolve_tool("ffprobe")
    command = [
        ffprobe,
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=codec_name,channels,sample_rate:format=duration,format_name",
        "-of",
        "json",
        str(path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", shell=False)
    if completed.returncode != 0:
        raise AudioToolError(f"FFprobe could not inspect {path}: {completed.stderr.strip()}")
    payload = json.loads(completed.stdout)
    streams = payload.get("streams") or []
    if not streams:
        raise AudioToolError(f"No audio stream found: {path}")
    stream = streams[0]
    metadata = payload.get("format") or {}
    return {
        "format": path.suffix.lower().lstrip("."),
        "codec": stream.get("codec_name"),
        "duration_seconds": round(float(metadata.get("duration", 0.0)), 6),
        "channels": int(stream.get("channels", 0)),
        "sample_rate_hz": int(stream.get("sample_rate", 0)),
        "peak_dbfs": None,
        "rms_dbfs": None,
        "leading_silence_ms": None,
        "trailing_silence_ms": None,
        "analysis_note": "Compressed-file waveform metrics require decode; convert an approved copy before final QA.",
    }


def inspect_audio(path: Path | str) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise AudioToolError(f"Audio source not found: {source}")
    suffix = source.suffix.lower()
    if suffix not in {".wav", ".mp3", ".ogg"}:
        raise AudioToolError(f"Unsupported audio format '{suffix}'; expected WAV, MP3, or OGG")
    report = _inspect_wav(source) if suffix == ".wav" else _inspect_with_ffprobe(source)
    report.update(
        {
            "filename": source.name,
            "source_path": str(source.resolve()),
            "source_sha256": file_sha256(source),
            "size_bytes": source.stat().st_size,
        }
    )
    return report


def _read_pcm_wav(path: Path) -> tuple[int, int, int, list[int]]:
    if path.suffix.lower() != ".wav":
        raise AudioToolError("Deterministic DSP currently requires a PCM .wav source")
    try:
        with wave.open(str(path), "rb") as wav:
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            sample_rate = wav.getframerate()
            frame_count = wav.getnframes()
            compression = wav.getcomptype()
            raw = wav.readframes(frame_count)
    except (wave.Error, EOFError) as exc:
        raise AudioToolError(f"Invalid WAV file: {path}: {exc}") from exc
    if compression != "NONE":
        raise AudioToolError("Deterministic DSP requires uncompressed PCM WAV")
    if sample_width != 2:
        raise AudioToolError("Deterministic DSP currently supports 16-bit PCM WAV only")
    return channels, sample_width, sample_rate, _decode_pcm(raw, sample_width)


def process_wav(
    source: Path | str,
    destination: Path | str,
    *,
    approved: bool,
    trim_threshold_dbfs: float = -60.0,
    fade_ms: float = 5.0,
    target_peak_dbfs: float = -1.0,
) -> dict[str, Any]:
    """Create an approved, non-overwriting processed WAV copy; never edit the source."""
    if not approved:
        raise AudioToolError("WAV processing requires an approved mapping; inspect and confirm the mapping first.")
    source_path = Path(source)
    destination_path = Path(destination)
    if not source_path.is_file():
        raise AudioToolError(f"Audio source not found: {source_path}")
    if destination_path.exists():
        raise AudioToolError(f"Refusing to overwrite existing output: {destination_path}")
    if destination_path.suffix.lower() != ".wav":
        raise AudioToolError("Processed intermediate output must use the .wav extension")
    if fade_ms < 0 or target_peak_dbfs > 0:
        raise AudioToolError("fade_ms must be non-negative and target_peak_dbfs must be at most 0")

    source_hash = file_sha256(source_path)
    channels, sample_width, sample_rate, samples = _read_pcm_wav(source_path)
    full_scale = float(1 << (sample_width * 8 - 1))
    threshold = full_scale * 10 ** (trim_threshold_dbfs / 20.0)
    frame_peaks = [
        max(abs(value) for value in samples[offset : offset + channels])
        for offset in range(0, len(samples), channels)
    ]
    first = next((index for index, value in enumerate(frame_peaks) if value > threshold), len(frame_peaks))
    last = next((index for index in range(len(frame_peaks) - 1, -1, -1) if frame_peaks[index] > threshold), -1)
    if last < first:
        raise AudioToolError("No samples exceed the trim threshold")
    processed = samples[first * channels : (last + 1) * channels]
    operations = ["trim_silence"]

    frame_count = len(processed) // channels
    fade_frames = min(int(round(sample_rate * fade_ms / 1000.0)), frame_count // 2)
    if fade_frames > 0:
        for frame in range(fade_frames):
            gain = frame / fade_frames
            for channel in range(channels):
                processed[frame * channels + channel] = round(processed[frame * channels + channel] * gain)
                tail = (frame_count - 1 - frame) * channels + channel
                processed[tail] = round(processed[tail] * gain)
        operations.append("fade_in_out")

    peak = max((abs(value) for value in processed), default=0)
    if peak <= 0:
        raise AudioToolError("Processed WAV contains no audible samples")
    target_peak = full_scale * 10 ** (target_peak_dbfs / 20.0)
    gain = target_peak / peak
    processed = [max(-32768, min(32767, round(value * gain))) for value in processed]
    operations.append("peak_normalize")

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    raw = struct.pack(f"<{len(processed)}h", *processed)
    try:
        with wave.open(str(destination_path), "wb") as wav:
            wav.setnchannels(channels)
            wav.setsampwidth(sample_width)
            wav.setframerate(sample_rate)
            wav.writeframes(raw)
    except (OSError, wave.Error):
        if destination_path.exists():
            destination_path.unlink()
        raise
    if file_sha256(source_path) != source_hash:
        if destination_path.exists():
            destination_path.unlink()
        raise AudioToolError("Source audio changed during processing; stop and restore the source")
    return {
        "source_file": str(source_path.resolve()),
        "source_sha256": source_hash,
        "output_file": str(destination_path.resolve()),
        "output_sha256": file_sha256(destination_path),
        "operations": operations,
        "trimmed_frames": first + (len(frame_peaks) - last - 1),
        "fade_ms": fade_ms,
        "target_peak_dbfs": target_peak_dbfs,
    }


def analyze_loop_seam(path: Path | str, *, window_ms: float = 10.0) -> dict[str, Any]:
    """Measure the sample difference between equally sized start/end loop windows."""
    source = Path(path)
    if not source.is_file():
        raise AudioToolError(f"Audio source not found: {source}")
    channels, sample_width, sample_rate, samples = _read_pcm_wav(source)
    frame_count = len(samples) // channels
    compared_frames = min(max(1, int(round(sample_rate * window_ms / 1000.0))), frame_count // 2)
    sample_count = compared_frames * channels
    differences = [abs(left - right) for left, right in zip(samples[:sample_count], samples[-sample_count:])]
    rms_difference = math.sqrt(sum(value * value for value in differences) / len(differences)) if differences else 0.0
    full_scale = float(1 << (sample_width * 8 - 1))
    return {
        "source_file": str(source.resolve()),
        "source_sha256": file_sha256(source),
        "window_ms": window_ms,
        "compared_frames": compared_frames,
        "seam_difference_dbfs": _dbfs(rms_difference, full_scale),
        "peak_difference_dbfs": _dbfs(float(max(differences, default=0)), full_scale),
    }


def versioned_output_path(folder: Path | str, stem: str, suffix: str) -> Path:
    destination = Path(folder) / f"{stem}{suffix}"
    version = 2
    while destination.exists():
        destination = Path(folder) / f"{stem}_v{version}{suffix}"
        version += 1
    return destination


def build_ffmpeg_command(
    ffmpeg: str,
    source: Path,
    destination: Path,
    *,
    positional: bool,
    quality: int = 5,
) -> list[str]:
    command = [ffmpeg, "-hide_banner", "-nostdin", "-n", "-i", str(source), "-vn"]
    if positional:
        command.extend(["-ac", "1"])
    command.extend(["-c:a", "libvorbis", "-q:a", str(quality), str(destination)])
    return command


def convert_audio(
    source: Path | str,
    destination: Path | str,
    *,
    approved: bool,
    positional: bool = True,
    quality: int = 5,
) -> dict[str, Any]:
    if not approved:
        raise AudioToolError("Conversion requires an approved mapping; inspect and confirm the mapping first.")
    source_path = Path(source)
    destination_path = Path(destination)
    if not source_path.is_file():
        raise AudioToolError(f"Audio source not found: {source_path}")
    if destination_path.exists():
        raise AudioToolError(f"Refusing to overwrite existing output: {destination_path}")
    if destination_path.suffix.lower() != ".ogg":
        raise AudioToolError("Minecraft delivery output must use the .ogg extension")
    before = file_sha256(source_path)
    ffmpeg = resolve_tool("ffmpeg")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    command = build_ffmpeg_command(ffmpeg, source_path, destination_path, positional=positional, quality=quality)
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", shell=False)
    if completed.returncode != 0 or not destination_path.is_file():
        if destination_path.exists():
            destination_path.unlink()
        raise AudioToolError(f"FFmpeg conversion failed: {completed.stderr.strip()}")
    if file_sha256(source_path) != before:
        raise AudioToolError("Source audio changed during conversion; stop and restore the source")
    return {
        "source_file": str(source_path.resolve()),
        "source_sha256": before,
        "output_file": str(destination_path.resolve()),
        "output_sha256": file_sha256(destination_path),
        "positional_mono": positional,
        "ffmpeg_command": command,
    }


def _write_json(payload: Any, destination: Path | None) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if destination is None:
        sys.stdout.write(text)
        return
    if destination.exists():
        raise AudioToolError(f"Refusing to overwrite existing report: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8", newline="\n")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect source audio without modifying it")
    inspect_parser.add_argument("inputs", nargs="+", type=Path)
    inspect_parser.add_argument("--json-out", type=Path)

    convert_parser = subparsers.add_parser("convert", help="Convert one approved source to versioned OGG")
    convert_parser.add_argument("source", type=Path)
    convert_parser.add_argument("destination", type=Path)
    convert_parser.add_argument("--approved", action="store_true")
    convert_parser.add_argument("--non-positional", action="store_true")
    convert_parser.add_argument("--quality", type=int, choices=range(0, 11), default=5)

    process_parser = subparsers.add_parser("process-wav", help="Trim, fade, and peak-normalize one approved WAV copy")
    process_parser.add_argument("source", type=Path)
    process_parser.add_argument("destination", type=Path)
    process_parser.add_argument("--approved", action="store_true")
    process_parser.add_argument("--trim-threshold-dbfs", type=float, default=-60.0)
    process_parser.add_argument("--fade-ms", type=float, default=5.0)
    process_parser.add_argument("--target-peak-dbfs", type=float, default=-1.0)

    seam_parser = subparsers.add_parser("loop-seam", help="Analyze the start/end seam of a PCM WAV loop")
    seam_parser.add_argument("source", type=Path)
    seam_parser.add_argument("--window-ms", type=float, default=10.0)

    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "inspect":
            _write_json([inspect_audio(path) for path in args.inputs], args.json_out)
        elif args.command == "convert":
            _write_json(
                convert_audio(
                    args.source,
                    args.destination,
                    approved=args.approved,
                    positional=not args.non_positional,
                    quality=args.quality,
                ),
                None,
            )
        elif args.command == "process-wav":
            _write_json(
                process_wav(
                    args.source,
                    args.destination,
                    approved=args.approved,
                    trim_threshold_dbfs=args.trim_threshold_dbfs,
                    fade_ms=args.fade_ms,
                    target_peak_dbfs=args.target_peak_dbfs,
                ),
                None,
            )
        else:
            _write_json(analyze_loop_seam(args.source, window_ms=args.window_ms), None)
    except (AudioToolError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
