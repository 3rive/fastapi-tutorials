from datetime import UTC, datetime
from typing import Any, Protocol

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.domain.user import User
from app.exceptions import ConflictError, NotFoundError
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(Protocol):
    async def create(self, payload: UserCreate) -> User: ...

    async def get_by_id(self, user_id: str) -> User: ...

    async def list_users(self, skip: int, limit: int) -> list[User]: ...

    async def update(self, user_id: str, payload: UserUpdate) -> User: ...

    async def delete(self, user_id: str) -> None: ...


def _to_domain(document: dict[str, Any]) -> User:
    return User(
        id=str(document["_id"]),
        email=document["email"],
        full_name=document["full_name"],
        phone=document.get("phone"),
        created_at=document["created_at"],
        updated_at=document["updated_at"],
    )


class MongoUserRepository:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._collection = database.users

    async def create(self, payload: UserCreate) -> User:
        now = datetime.now(UTC)
        document = {
            "email": payload.email.lower(),
            "full_name": payload.full_name.strip(),
            "phone": payload.phone,
            "created_at": now,
            "updated_at": now,
        }
        try:
            result = await self._collection.insert_one(document)
        except DuplicateKeyError:
            raise ConflictError("A user with this email already exists") from None
        document["_id"] = result.inserted_id
        return _to_domain(document)

    async def get_by_id(self, user_id: str) -> User:
        object_id = _parse_object_id(user_id)
        document = await self._collection.find_one({"_id": object_id})
        if document is None:
            raise NotFoundError("User not found")
        return _to_domain(document)

    async def list_users(self, skip: int, limit: int) -> list[User]:
        cursor = (
            self._collection.find({})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        return [_to_domain(document) async for document in cursor]

    async def update(self, user_id: str, payload: UserUpdate) -> User:
        object_id = _parse_object_id(user_id)
        updates: dict[str, Any] = {}
        if payload.email is not None:
            updates["email"] = payload.email.lower()
        if payload.full_name is not None:
            updates["full_name"] = payload.full_name.strip()
        if payload.phone is not None:
            updates["phone"] = payload.phone
        if not updates:
            return await self.get_by_id(user_id)

        updates["updated_at"] = datetime.now(UTC)
        try:
            result = await self._collection.find_one_and_update(
                {"_id": object_id},
                {"$set": updates},
                return_document=ReturnDocument.AFTER,
            )
        except DuplicateKeyError:
            raise ConflictError("A user with this email already exists") from None
        if result is None:
            raise NotFoundError("User not found")
        return _to_domain(result)

    async def delete(self, user_id: str) -> None:
        object_id = _parse_object_id(user_id)
        result = await self._collection.delete_one({"_id": object_id})
        if result.deleted_count == 0:
            raise NotFoundError("User not found")


def _parse_object_id(user_id: str) -> ObjectId:
    try:
        return ObjectId(user_id)
    except InvalidId:
        raise NotFoundError("User not found") from None
