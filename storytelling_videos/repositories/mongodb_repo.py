from uuid import uuid4

from storytelling_videos.core.mongodb_core import get_stories_collection
from storytelling_videos.models.database_schema import StoryDB, StoryResponse


class MongoRepo:
    def __init__(self):
        self.collection = get_stories_collection()

    async def post_to_mongodb(self, story_db: StoryDB) -> StoryResponse:
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

    async def get_from_mongodb(self, uuid: str) -> StoryResponse:
        """Fetch a story from the database by uuid."""
        doc = await self.collection.find_one({"_id": uuid})
        if not doc:
            raise ValueError(f"Story with id {uuid} not found.")
        return StoryResponse(
            id=doc["_id"],
            topic=doc["topic"],
            content=doc["content"],
            model=doc["model"],
            created_at=doc["created_at"],
        )
