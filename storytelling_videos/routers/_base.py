from fastapi import APIRouter

from storytelling_videos.routers.openrouter_router import router as OpenRouter

# Create a combined router for all routes
router = APIRouter()
router.include_router(OpenRouter, prefix="/stories", tags=["stories"])

__all__ = ["router"]
