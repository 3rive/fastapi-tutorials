from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.repositories.entitlement_repository import (
    EntitlementRepository,
    InMemoryEntitlementRepository,
)
from app.repositories.user_repository import MongoUserRepository, UserRepository
from app.services.entitlement_service import EntitlementService
from app.services.user_service import UserService


async def get_db() -> AsyncIterator[AsyncIOMotorDatabase]:
    yield get_database()


def get_user_repository(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> UserRepository:
    return MongoUserRepository(database)


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(repository)


def get_entitlement_repository() -> EntitlementRepository:
    return InMemoryEntitlementRepository()


def get_entitlement_service(
    repository: Annotated[EntitlementRepository, Depends(get_entitlement_repository)],
) -> EntitlementService:
    return EntitlementService(repository)
