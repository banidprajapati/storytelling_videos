from functools import lru_cache

from pymongo import AsyncMongoClient

from storytelling_videos.core.config_core import settings


@lru_cache(maxsize=1)
def get_mongo_client():
    # Add connection parameters to help with DNS resolution
    client = AsyncMongoClient(
        settings.MONGODB_URI,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000,
        maxPoolSize=10,
        retryWrites=True,
    )
    return client


def get_mongo_database():
    client = get_mongo_client()
    return client[settings.MONGODB_DB]


def get_stories_collection():
    db = get_mongo_database()
    return db["stories"]


async def close_mongo_client():
    client = get_mongo_client()
    try:
        await client.close()
    finally:
        get_mongo_client.cache_clear()
