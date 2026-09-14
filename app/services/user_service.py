from loguru import logger

from app.domain.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def create_user(self, payload: UserCreate) -> UserResponse:
        logger.info("Creating user with email={}", payload.email)
        user = await self._repository.create(payload)
        return _to_response(user)

    async def get_user(self, user_id: str) -> UserResponse:
        user = await self._repository.get_by_id(user_id)
        return _to_response(user)

    async def list_users(self, skip: int, limit: int) -> list[UserResponse]:
        users = await self._repository.list_users(skip=skip, limit=limit)
        return [_to_response(user) for user in users]

    async def update_user(self, user_id: str, payload: UserUpdate) -> UserResponse:
        logger.info("Updating user id={}", user_id)
        user = await self._repository.update(user_id, payload)
        return _to_response(user)

    async def delete_user(self, user_id: str) -> None:
        logger.info("Deleting user id={}", user_id)
        await self._repository.delete(user_id)


def _to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
