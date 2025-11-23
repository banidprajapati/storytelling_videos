from fastapi import APIRouter, HTTPException

from storytelling_videos.core.loggings import get_logger
from storytelling_videos.models import StoryCreate, StoryDB, StoryResponse
from storytelling_videos.repositories.mongodb_repo import MongoRepo
from storytelling_videos.services.openrouter_service import OpenRouterService

logger = get_logger(__name__)

router = APIRouter()
mongo_class = MongoRepo()


@router.post("/generate_script", response_model=StoryResponse)
async def generate_story(story_create: StoryCreate) -> StoryResponse:
    """Generate a new story from a topic.
    Store the story to the database.
    """
    try:
        # Generate story from OpenRouter API
        content = await OpenRouterService.generate_story(
            prompt=story_create.prompt,
            model=story_create.model,
        )

        # Save to database
        story_db = StoryDB(
            topic=story_create.prompt,
            content=content,
            model=story_create.model,
        )
        response = await mongo_class.post_to_mongodb(story_db=story_db)
        logger.info(f"Story generated and saved: {response.id}")
        return response
    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        raise


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(story_uuid: str) -> StoryResponse:
    """Get a story by ID."""
    story = await mongo_class.get_from_mongodb(story_uuid)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story
