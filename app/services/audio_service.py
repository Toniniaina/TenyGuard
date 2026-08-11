import os
import shutil
import subprocess
import wave
from pathlib import Path
from typing import Optional
from app.core.logging import logger


class AudioExtractionError(Exception):
    """Exception raised when FFmpeg fails to extract audio."""
    pass


class AudioService:
    """
    Service responsible for extracting, converting, and analyzing audio tracks from video files using FFmpeg.
    Optimized for Speech-To-Text (Mono, 16kHz WAV PCM).
    """

    def __init__(self, output_dir: str = "data/audio", sample_rate: int = 16000):
        self.output_dir = Path(output_dir)
        self.sample_rate = sample_rate
        self._ensure_output_directory()
        self._check_and_register_winget_path()

    def _ensure_output_directory(self) -> None:
        """Ensures the destination audio directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _check_and_register_winget_path(self) -> None:
        """
        Fallback for Windows: If FFmpeg was installed via WinGet/Chocolatey during session,
        registers common executable paths into OS environment PATH if not present.
        """
        if shutil.which("ffmpeg") is None:
            local_appdata = os.environ.get("LOCALAPPDATA", "")
            winget_links = Path(local_appdata) / "Microsoft" / "WinGet" / "Links"
            ffmpeg_executable = winget_links / "ffmpeg.exe"
            
            if ffmpeg_executable.exists():
                os.environ["PATH"] = str(winget_links) + os.pathsep + os.environ.get("PATH", "")
                logger.info(f"Registered WinGet FFmpeg path: {winget_links}")

    def is_ffmpeg_available(self) -> bool:
        """Checks if FFmpeg binary is available on the system PATH."""
        self._check_and_register_winget_path()
        return shutil.which("ffmpeg") is not None

    def extract_audio(self, video_path: str, output_filename: Optional[str] = None) -> str:
        """
        Extracts audio from input video file to WAV 16kHz mono format using FFmpeg.

        :param video_path: Path to the source video file.
        :param output_filename: Optional custom output filename (e.g. 'audio_123.wav').
        :return: Path to the generated audio file (.wav).
        :raises FileNotFoundError: If source video file does not exist.
        :raises AudioExtractionError: If FFmpeg execution fails or FFmpeg is not installed.
        """
        video_file = Path(video_path)
        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if not self.is_ffmpeg_available():
            logger.error("FFmpeg binary is not found on system PATH.")
            raise AudioExtractionError(
                "FFmpeg n'est pas installé ou introuvable dans le PATH système. "
                "Veuillez installer FFmpeg (https://ffmpeg.org/download.html)."
            )

        # Build output WAV path
        if not output_filename:
            output_filename = f"{video_file.stem}_audio.wav"
        elif not output_filename.endswith(".wav"):
            output_filename = f"{output_filename}.wav"

        audio_path = self.output_dir / output_filename

        # FFmpeg command optimized for Whisper / STT: Mono (-ac 1), 16kHz (-ar 16000), PCM 16-bit
        command = [
            "ffmpeg",
            "-y",                   # Overwrite output file without asking
            "-i", str(video_file),   # Input video
            "-vn",                  # Disable video recording (audio only)
            "-acodec", "pcm_s16le", # 16-bit PCM audio codec
            "-ar", str(self.sample_rate), # 16000 Hz sample rate
            "-ac", "1",             # Mono channel
            str(audio_path)
        ]

        logger.info(f"Extracting audio from '{video_path}' -> '{audio_path}'...")
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            logger.info(f"Audio extraction successful: '{audio_path}'")
            return str(audio_path.resolve())

        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg failed with exit code {e.returncode}: {e.stderr}"
            logger.error(error_msg)
            raise AudioExtractionError(error_msg) from e

    def get_audio_duration(self, audio_path: str) -> float:
        """
        Calculates duration (in seconds) of a WAV audio file.
        Uses Python's standard 'wave' module or ffprobe fallback.
        """
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            with wave.open(str(path), 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)
                return round(duration, 2)
        except Exception:
            # Fallback to ffprobe if wave module fails
            if shutil.which("ffprobe"):
                cmd = [
                    "ffprobe", "-v", "error", "-show_entries",
                    "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
                    str(path)
                ]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if res.returncode == 0:
                    return round(float(res.stdout.strip()), 2)
            return 0.0

    def cleanup_audio(self, audio_path: str) -> bool:
        """
        Deletes a temporary audio file from disk.
        """
        path = Path(audio_path)
        if path.exists():
            try:
                path.unlink()
                logger.info(f"Cleaned up audio file: '{audio_path}'")
                return True
            except Exception as e:
                logger.warning(f"Failed to delete audio file '{audio_path}': {e}")
                return False
        return False
