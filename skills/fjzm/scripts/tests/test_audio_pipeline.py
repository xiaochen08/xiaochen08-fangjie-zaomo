import hashlib
import importlib.util
import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "audio_pipeline.py"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError("audio_pipeline.py is missing")
    spec = importlib.util.spec_from_file_location("audio_pipeline", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_test_wav(path: Path) -> None:
    sample_rate = 8000
    frames = []
    for index in range(2000):
        if index < 400 or index >= 1600:
            sample = 0
        else:
            sample = int(16384 * math.sin(2 * math.pi * 440 * index / sample_rate))
        frames.append(struct.pack("<h", sample))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"".join(frames))


class AudioPipelineTests(unittest.TestCase):
    def test_inspects_real_wav_and_preserves_source(self):
        audio = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "炮塔启动.wav"
            make_test_wav(source)
            before = hashlib.sha256(source.read_bytes()).hexdigest()

            report = audio.inspect_audio(source)

            self.assertEqual(report["filename"], "炮塔启动.wav")
            self.assertEqual(report["format"], "wav")
            self.assertEqual(report["channels"], 1)
            self.assertEqual(report["sample_rate_hz"], 8000)
            self.assertAlmostEqual(report["duration_seconds"], 0.25, places=3)
            self.assertLessEqual(report["peak_dbfs"], -5.9)
            self.assertGreaterEqual(report["leading_silence_ms"], 45)
            self.assertGreaterEqual(report["trailing_silence_ms"], 45)
            self.assertEqual(report["source_sha256"], before)
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)

    def test_allocates_versioned_output_without_overwrite(self):
        audio = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.assertEqual(audio.versioned_output_path(folder, "fire", ".ogg").name, "fire.ogg")
            (folder / "fire.ogg").write_bytes(b"existing")
            self.assertEqual(audio.versioned_output_path(folder, "fire", ".ogg").name, "fire_v2.ogg")

    def test_conversion_requires_mapping_approval_before_tool_lookup(self):
        audio = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "01.wav"
            make_test_wav(source)
            before = source.read_bytes()
            with self.assertRaisesRegex(audio.AudioToolError, "approved mapping"):
                audio.convert_audio(source, Path(tmp) / "out.ogg", approved=False)
            self.assertEqual(source.read_bytes(), before)

    def test_missing_external_tool_has_actionable_error(self):
        audio = load_module()
        with self.assertRaisesRegex(audio.AudioToolError, "not found"):
            audio.resolve_tool("definitely-not-a-real-audio-tool-9f3f")

    def test_ffmpeg_command_is_argument_list_and_defaults_positional_audio_to_mono(self):
        audio = load_module()
        command = audio.build_ffmpeg_command(
            "ffmpeg", Path("input.wav"), Path("output.ogg"), positional=True
        )
        self.assertIsInstance(command, list)
        self.assertIn("-ac", command)
        self.assertEqual(command[command.index("-ac") + 1], "1")
        self.assertNotIn("shell=True", command)

    def test_processes_approved_wav_copy_with_trim_fades_and_peak_normalization(self):
        audio = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "蓄能.wav"
            output = Path(tmp) / "processed.wav"
            make_test_wav(source)
            before = hashlib.sha256(source.read_bytes()).hexdigest()
            report = audio.process_wav(
                source,
                output,
                approved=True,
                trim_threshold_dbfs=-60.0,
                fade_ms=5.0,
                target_peak_dbfs=-1.0,
            )
            inspected = audio.inspect_audio(output)
            self.assertLess(inspected["duration_seconds"], 0.2)
            self.assertAlmostEqual(inspected["peak_dbfs"], -1.0, delta=0.15)
            self.assertIn("trim_silence", report["operations"])
            self.assertIn("fade_in_out", report["operations"])
            self.assertIn("peak_normalize", report["operations"])
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)

    def test_wav_processing_refuses_unapproved_or_existing_destination(self):
        audio = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.wav"
            output = Path(tmp) / "processed.wav"
            make_test_wav(source)
            with self.assertRaisesRegex(audio.AudioToolError, "approved mapping"):
                audio.process_wav(source, output, approved=False)
            output.write_bytes(b"existing")
            with self.assertRaisesRegex(audio.AudioToolError, "overwrite"):
                audio.process_wav(source, output, approved=True)

    def test_loop_seam_analysis_reports_perfect_constant_seam(self):
        audio = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "loop.wav"
            with wave.open(str(source), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(8000)
                wav.writeframes(struct.pack("<h", 4000) * 800)
            report = audio.analyze_loop_seam(source, window_ms=10.0)
            self.assertEqual(report["compared_frames"], 80)
            self.assertIsNone(report["seam_difference_dbfs"])


if __name__ == "__main__":
    unittest.main()
