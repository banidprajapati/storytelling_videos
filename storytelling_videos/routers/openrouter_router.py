from fastapi import APIRouter, HTTPException

from storytelling_videos.core.loggings import get_logger
from storytelling_videos.models import StoryCreate, StoryDB, StoryResponse
from storytelling_videos.repositories.openrouter_repo import StoryRepository
from storytelling_videos.services.openrouter_service import OpenRouterService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/stories", tags=["stories"])
story_repo = StoryRepository()


@router.post("/generate", response_model=StoryResponse)
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
        response = await story_repo.create_story(story_db=story_db)
        logger.info(f"Story generated and saved: {response.id}")
        return response
    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        raise


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(story_id: str) -> StoryResponse:
    """Get a story by ID."""
    story = await story_repo.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story


@router.get("", response_model=list[StoryResponse])
async def list_stories(skip: int = 0, limit: int = 10) -> list[StoryResponse]:
    """List all stories with pagination."""
    return await story_repo.list_stories(limit=limit, skip=skip)
