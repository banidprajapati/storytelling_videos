from fastapi import APIRouter

from storytelling_videos.routers.kokoro_tts_router import router as KokoroRouter
from storytelling_videos.routers.mongo_router import router as MongoRouter

# Create a combined router for all routes
router = APIRouter()
router.include_router(MongoRouter, prefix="/stories", tags=["stories"])
router.include_router(KokoroRouter, prefix="/tts", tags=["TTS"])

__all__ = ["router"]
