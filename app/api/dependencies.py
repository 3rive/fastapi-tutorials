from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.application.services.user_service import UserService
from app.domain.ports.user_repository import UserRepositoryPort
from app.infrastructure.persistence.mongodb.database import get_database
from app.infrastructure.persistence.mongodb.user_repository import MongoUserRepository


async def get_db() -> AsyncIterator[AsyncIOMotorDatabase]:
    yield get_database()


def get_user_repository(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> UserRepositoryPort:
    return MongoUserRepository(database)


def get_user_service(
    repository: Annotated[UserRepositoryPort, Depends(get_user_repository)],
) -> UserService:
    return UserService(repository)
