from datetime import datetime

from pydantic import BaseModel, Field


class StoryCreate(BaseModel):
    """Schema for creating a new story."""

    prompt: str = Field(..., description="Topic or prompt for the story")
    model: str = Field(
        "x-ai/grok-4.1-fast",
        description="Model to use for generation",
    )


class StoryResponse(BaseModel):
    """Schema for story response."""

    id: str = Field(..., description="Story ID")
    topic: str = Field(..., description="Topic of the story")
    content: str = Field(..., description="Generated story content")
    model: str = Field(..., description="Model used")
    created_at: datetime = Field(..., description="Creation timestamp")


class StoryDB(BaseModel):
    """Schema for database storage."""

    topic: str
    content: str
    model: str
    created_at: datetime = Field(default_factory=datetime.now)
