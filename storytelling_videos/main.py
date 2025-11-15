from contextlib import asynccontextmanager

# import uvicorn
from fastapi import FastAPI

from storytelling_videos.core.config_core import settings
from storytelling_videos.core.loggings import get_logger
from storytelling_videos.core.mongodb_core import close_mongo_client, get_mongo_client

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Vertex Face Attendance API.")
    # Startup phase
    get_mongo_client()

    yield

    await close_mongo_client()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="This project takes stories from llm and converts it into tiktok reddit videos.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router)
