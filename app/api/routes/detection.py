from fastapi import APIRouter, Depends
from app.api.dependencies import get_profanity_service
from app.models.detection import DetectionRequest, DetectionResponse
from app.services.profanity_service import ProfanityService

router = APIRouter(prefix="/detection", tags=["Detection"])


@router.post("/analyze", response_model=DetectionResponse, summary="Analyze Video or Text for Profanity")
def analyze_detection(
    request: DetectionRequest,
    profanity_service: ProfanityService = Depends(get_profanity_service)
):
    """
    Triggers Malagasy profanity detection on video transcription.
    """
    # Skeleton detection endpoint
    return DetectionResponse(
        video_id=request.video_id,
        detections=[],
        total_detections=0
    )
