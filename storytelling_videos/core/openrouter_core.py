from functools import lru_cache

import httpx

from storytelling_videos.core.config_core import settings


@lru_cache(maxsize=1)
def get_openrouter_client() -> httpx.AsyncClient:
    """Get or create an OpenRouter API client."""
    return httpx.AsyncClient(
        base_url="https://openrouter.ai/api/v1",
        headers={
            "Authorization": f"Bearer {settings.OPENROUTER_API}",
        },
        timeout=30.0,
    )


async def close_openrouter_client():
    """Close the OpenRouter client."""
    client = get_openrouter_client()
    try:
        await client.aclose()
    finally:
        get_openrouter_client.cache_clear()
