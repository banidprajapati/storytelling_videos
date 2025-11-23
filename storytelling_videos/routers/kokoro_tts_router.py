from fastapi import APIRouter

from storytelling_videos.core.loggings import get_logger
from storytelling_videos.models import StoryResponse
from storytelling_videos.repositories.mongodb_repo import MongoRepo
from storytelling_videos.services.preprocess_text_service import add_pauses
from storytelling_videos.services.voice_kokoro_service import KokoroVoice

logger = get_logger(__name__)

router = APIRouter()
mongo_class = MongoRepo()


@router.post("/generate_tts", response_model=StoryResponse)
async def generate_tts(script_uuid: str) -> StoryResponse:
    """Generate TTS audio from a stored story."""
    try:
        story: StoryResponse = await mongo_class.get_from_mongodb(script_uuid)
        script = story.content  # Access content attribute from StoryResponse
        script_processed = add_pauses(script)
        kokoro = KokoroVoice(text=script_processed, voice="am_liam", lang_code="a", speed=1)
        generator = kokoro.synthesize()
        kokoro.save_audio(uuid=script_uuid, generator=generator)
        return story
    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}")
        raise
