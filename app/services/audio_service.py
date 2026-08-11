class AudioService:
    """
    Service responsible for audio extraction using FFmpeg.
    """

    def __init__(self, output_dir: str = "data/audio"):
        self.output_dir = output_dir

    def extract_audio(self, video_path: str) -> str:
        """
        Skeleton method: Extracts audio track from input video file to WAV format using FFmpeg.
        Returns extracted audio file path.
        """
        # FFmpeg command execution skeleton
        audio_filename = f"{self.output_dir}/extracted.wav"
        return audio_filename
