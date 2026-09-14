from loguru import logger

from app.domain.ports.user_repository import UserRepositoryPort
from app.domain.user import NewUser, User, UserChanges


class UserService:
    """Application layer: orchestrates use cases without HTTP or persistence details."""

    def __init__(self, repository: UserRepositoryPort) -> None:
        self._repository = repository

    async def create_user(self, data: NewUser) -> User:
        logger.info("Creating user with email={}", data.email)
        return await self._repository.create(data)

    async def get_user(self, user_id: str) -> User:
        return await self._repository.get_by_id(user_id)

    async def list_users(self, skip: int, limit: int) -> list[User]:
        return await self._repository.list_users(skip=skip, limit=limit)

    async def update_user(self, user_id: str, changes: UserChanges) -> User:
        logger.info("Updating user id={}", user_id)
        return await self._repository.update(user_id, changes)

    async def delete_user(self, user_id: str) -> None:
        logger.info("Deleting user id={}", user_id)
        await self._repository.delete(user_id)
