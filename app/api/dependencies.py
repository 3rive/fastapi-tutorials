from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repositories.entitlement_repository import (
    EntitlementRepository,
    SqliteEntitlementRepository,
)
from app.repositories.user_repository import SqliteUserRepository, UserRepository
from app.services.entitlement_service import EntitlementService
from app.services.user_service import UserService


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return SqliteUserRepository(session)


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(repository)


def get_entitlement_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EntitlementRepository:
    return SqliteEntitlementRepository(session)


def get_entitlement_service(
    repository: Annotated[EntitlementRepository, Depends(get_entitlement_repository)],
) -> EntitlementService:
    return EntitlementService(repository)
