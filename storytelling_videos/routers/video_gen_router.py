from fastapi import APIRouter, HTTPException

from storytelling_videos.core.loggings import get_logger
from storytelling_videos.services.video_gen_service import VideoGeneration

logger = get_logger(__name__)

router = APIRouter()


@router.post("/generate_video")
async def generate_video(script_uuid: str, stock_video_path: str = None) -> dict:
    """Generate final video with embedded subtitles.

    Args:
        script_uuid: UUID of the script/story
        stock_video_path: Optional path to specific stock video. If None, random one is selected.

    Returns:
        Dictionary with path to generated video
    """
    try:
        # Generate video
        video_gen = VideoGeneration(script_uuid=script_uuid)
        video_gen.generate(stock_video_path=stock_video_path)

        logger.info(f"Video generated successfully at: {video_gen.output_path}")

        return {
            "status": "success",
            "script_uuid": script_uuid,
            "video_path": str(video_gen.output_path),
            "message": "Video with embedded subtitles generated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating video: {str(e)}")
