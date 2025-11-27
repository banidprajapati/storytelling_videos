from fastapi import APIRouter, HTTPException

from storytelling_videos.core.loggings import get_logger
from storytelling_videos.services.whisperx_service import WhisperXSubtitleGenerator

logger = get_logger(__name__)

router = APIRouter()


@router.post("/generate_srt")
async def generate_srt(script_uuid: str, model_name: str = "tiny") -> dict:
    """Generate word-level SRT subtitles from audio using WhisperX.

    Args:
        script_uuid: UUID of the script/story
        model_name: Whisper model to use (tiny, base, small, medium, large)

    Returns:
        Dictionary with path to generated SRT file
    """
    try:
        # Generate word-level subtitles
        subtitle_generator = WhisperXSubtitleGenerator(
            script_uuid=script_uuid, model_name=model_name
        )
        srt_path = subtitle_generator.generate_word_level_srt()

        logger.info(f"SRT subtitles generated successfully at: {srt_path}")

        return {
            "status": "success",
            "script_uuid": script_uuid,
            "srt_path": str(srt_path),
            "message": "Word-level SRT subtitles generated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating SRT subtitles: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error generating SRT subtitles: {str(e)}"
        )
