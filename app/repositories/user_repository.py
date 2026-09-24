from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user import User
from app.exceptions import ConflictError, NotFoundError
from app.models.user import UserRow
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(Protocol):
    async def create(self, payload: UserCreate) -> User: ...

    async def get_by_id(self, user_id: str) -> User: ...

    async def list_users(self, skip: int, limit: int) -> list[User]: ...

    async def update(self, user_id: str, payload: UserUpdate) -> User: ...

    async def delete(self, user_id: str) -> None: ...


def _to_domain(row: UserRow) -> User:
    return User(
        id=row.id,
        email=row.email,
        full_name=row.full_name,
        phone=row.phone,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class SqliteUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, payload: UserCreate) -> User:
        now = datetime.now(UTC)
        row = UserRow(
            email=payload.email.lower(),
            full_name=payload.full_name.strip(),
            phone=payload.phone,
            created_at=now,
            updated_at=now,
        )
        self._session.add(row)
        try:
            await self._session.flush()
        except IntegrityError:
            raise ConflictError("A user with this email already exists") from None
        return _to_domain(row)

    async def get_by_id(self, user_id: str) -> User:
        row = await self._session.get(UserRow, user_id)
        if row is None:
            raise NotFoundError("User not found")
        return _to_domain(row)

    async def list_users(self, skip: int, limit: int) -> list[User]:
        result = await self._session.execute(
            select(UserRow).order_by(UserRow.created_at.desc()).offset(skip).limit(limit)
        )
        return [_to_domain(row) for row in result.scalars().all()]

    async def update(self, user_id: str, payload: UserUpdate) -> User:
        row = await self._session.get(UserRow, user_id)
        if row is None:
            raise NotFoundError("User not found")
        if payload.email is not None:
            row.email = payload.email.lower()
        if payload.full_name is not None:
            row.full_name = payload.full_name.strip()
        if payload.phone is not None:
            row.phone = payload.phone
        row.updated_at = datetime.now(UTC)
        try:
            await self._session.flush()
        except IntegrityError:
            raise ConflictError("A user with this email already exists") from None
        return _to_domain(row)

    async def delete(self, user_id: str) -> None:
        row = await self._session.get(UserRow, user_id)
        if row is None:
            raise NotFoundError("User not found")
        await self._session.delete(row)
        await self._session.flush()
