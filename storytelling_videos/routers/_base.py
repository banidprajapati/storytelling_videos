from fastapi import APIRouter

from storytelling_videos.routers.kokoro_tts_router import router as KokoroRouter
from storytelling_videos.routers.mongo_router import router as MongoRouter
from storytelling_videos.routers.orchestrate_router import router as OrchestrateRouter
from storytelling_videos.routers.srt_router import router as SRTRouter
from storytelling_videos.routers.video_gen_router import router as VideoGenRouter

# Create a combined router for all routes
router = APIRouter()
router.include_router(MongoRouter, prefix="/stories", tags=["stories"])
router.include_router(KokoroRouter, prefix="/tts", tags=["TTS"])
router.include_router(SRTRouter, prefix="/srt", tags=["subtitles"])
router.include_router(VideoGenRouter, prefix="/videos", tags=["videos"])
router.include_router(OrchestrateRouter, prefix="/pipeline", tags=["pipeline"])

__all__ = ["router"]
