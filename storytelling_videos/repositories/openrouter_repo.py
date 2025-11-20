from uuid import uuid4

from storytelling_videos.core.loggings import get_logger
from storytelling_videos.core.mongodb_core import get_stories_collection
from storytelling_videos.models import StoryDB, StoryResponse

logger = get_logger(__name__)


class StoryRepository:
    """Repository for story database operations."""

    def __init__(self):
        self.collection = get_stories_collection()

    async def create_story(self, story_db: StoryDB) -> StoryResponse:
        """Create a new story in the database."""
        story_id = str(uuid4())
        doc = story_db.model_dump(mode="json")
        doc["_id"] = story_id
        await self.collection.insert_one(doc)

        return StoryResponse(
            id=story_id,
            topic=story_db.topic,
            content=story_db.content,
            model=story_db.model,
            created_at=story_db.created_at,
        )

    async def get_story(self, story_id: str) -> StoryResponse | None:
        """Get a story by ID."""
        try:
            doc = await self.collection.find_one({"_id": story_id})
            if not doc:
                logger.warning(f"Story not found: {story_id}")
                return None

            return StoryResponse(
                id=str(doc["_id"]),
                topic=doc["topic"],
                content=doc["content"],
                model=doc["model"],
                created_at=doc["created_at"],
            )
        except Exception as e:
            logger.error(f"Error retrieving story {story_id}: {str(e)}")
            raise

    async def list_stories(self, limit: int = 10, skip: int = 0) -> list[StoryResponse]:
        """List all stories with pagination."""
        try:
            cursor = (
                self.collection.find().skip(skip).limit(limit).sort("created_at", -1)
            )
            stories = []
            async for doc in cursor:
                stories.append(
                    StoryResponse(
                        id=str(doc["_id"]),
                        topic=doc["topic"],
                        content=doc["content"],
                        model=doc["model"],
                        created_at=doc["created_at"],
                    )
                )
            logger.info(f"Retrieved {len(stories)} stories")
            return stories
        except Exception as e:
            logger.error(f"Error listing stories: {str(e)}")
            raise
