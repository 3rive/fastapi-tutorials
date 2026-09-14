from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import Settings, get_settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    if _client is None:
        raise RuntimeError("MongoDB client is not initialized")
    return _client


def get_database(settings: Settings | None = None) -> AsyncIOMotorDatabase:
    settings = settings or get_settings()
    return get_client()[settings.mongodb_database]


async def connect_to_mongo(settings: Settings | None = None) -> None:
    global _client
    settings = settings or get_settings()
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    await _client.admin.command("ping")


async def close_mongo_connection() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


async def ensure_indexes(database: AsyncIOMotorDatabase) -> None:
    await database.users.create_index("email", unique=True)


async def init_database() -> None:
    settings = get_settings()
    await connect_to_mongo(settings)
    await ensure_indexes(get_database(settings))
