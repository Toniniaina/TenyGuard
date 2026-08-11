from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.api.dependencies import get_video_service
from app.models.video import VideoResponse
from app.services.video_service import VideoService

router = APIRouter(prefix="/videos", tags=["Videos"])


@router.post("/upload", response_model=VideoResponse, summary="Upload Video for Analysis")
async def upload_video(
    file: UploadFile = File(...),
    video_service: VideoService = Depends(get_video_service)
):
    """
    Receives and validates input video file for profanity detection.
    """
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid video format.")

    # Skeleton handler
    video_res = video_service.save_video(
        filename=file.filename,
        content_type=file.content_type,
        content_length=0
    )
    return video_res


@router.get("/{video_id}", response_model=VideoResponse, summary="Get Video Status")
def get_video(
    video_id: str,
    video_service: VideoService = Depends(get_video_service)
):
    video_info = video_service.get_video_status(video_id)
    if not video_info:
        raise HTTPException(status_code=404, detail="Video not found.")
    return video_info
