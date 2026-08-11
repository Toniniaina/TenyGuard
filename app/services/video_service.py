import uuid
from typing import Optional
from app.models.video import VideoResponse


class VideoService:
    """
    Service responsible for managing video files and processing workflows.
    """

    def __init__(self, upload_dir: str = "data/videos"):
        self.upload_dir = upload_dir

    def save_video(self, filename: str, content_type: str, content_length: int) -> VideoResponse:
        """
        Skeleton method: Saves video metadata and prepares target file path.
        """
        video_id = str(uuid.uuid4())
        filepath = f"{self.upload_dir}/{video_id}_{filename}"
        return VideoResponse(
            id=video_id,
            filename=filename,
            content_type=content_type,
            filepath=filepath,
            status="uploaded"
        )

    def get_video_status(self, video_id: str) -> Optional[VideoResponse]:
        """
        Skeleton method: Retrieves processing status for a video.
        """
        return None
