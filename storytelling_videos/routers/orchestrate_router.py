from typing import Optional

from fastapi import APIRouter, HTTPException

from storytelling_videos.core.loggings import get_logger
from storytelling_videos.models import StoryResponse
from storytelling_videos.repositories.mongodb_repo import MongoRepo
from storytelling_videos.services.pipeline_service import VideoPipeline

logger = get_logger(__name__)

router = APIRouter()
mongo_class = MongoRepo()


@router.post("/orchestrate")
async def orchestrate_video_generation(
    script_uuid: str,
    voice: str = "am_liam",
    whisper_model: str = "tiny",
    speed: float = 1.0,
    stock_video_path: Optional[str] = None,
) -> dict:
    """
    Orchestrate the complete video generation pipeline.

    This endpoint handles the entire workflow:
    1. Fetch story from MongoDB
    2. Generate TTS audio from story content
    3. Generate word-level SRT subtitles using WhisperX
    4. Generate final video with embedded subtitles

    Args:
        script_uuid: UUID of the story/script
        voice: Voice for TTS (default: am_liam)
        whisper_model: Whisper model for subtitles (default: tiny)
        speed: Speech speed (default: 1.0)
        stock_video_path: Optional path to specific stock video

    Returns:
        Dictionary with all generated file paths and completion status
    """
    try:
        logger.info(f"[Orchestrate] Starting video generation for {script_uuid}")

        # Fetch story from database
        try:
            story: StoryResponse = await mongo_class.get_from_mongodb(script_uuid)
        except ValueError:
            raise HTTPException(
                status_code=404, detail=f"Story with UUID {script_uuid} not found"
            )

        # Create and run pipeline
        pipeline = VideoPipeline(script_uuid=script_uuid, script_content=story.content)

        result = pipeline.run_complete_pipeline(
            voice=voice,
            model_name=whisper_model,
            speed=speed,
            stock_video_path=stock_video_path,
        )

        logger.info(
            f"[Orchestrate] Video generation completed successfully for {script_uuid}"
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Orchestrate] Error during orchestration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error during video generation orchestration: {str(e)}",
        )
