from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.domain.exceptions import ConflictError, NotFoundError
from app.domain.user import NewUser, User, UserChanges


def _document_to_user(document: dict[str, Any]) -> User:
    return User(
        id=str(document["_id"]),
        email=document["email"],
        full_name=document["full_name"],
        phone=document.get("phone"),
        created_at=document["created_at"],
        updated_at=document["updated_at"],
    )


class MongoUserRepository:
    """Infrastructure adapter: maps domain operations to MongoDB documents."""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._collection = database.users

    async def create(self, data: NewUser) -> User:
        now = datetime.now(UTC)
        document = {
            "email": data.email,
            "full_name": data.full_name,
            "phone": data.phone,
            "created_at": now,
            "updated_at": now,
        }
        try:
            result = await self._collection.insert_one(document)
        except DuplicateKeyError:
            raise ConflictError("A user with this email already exists") from None
        document["_id"] = result.inserted_id
        return _document_to_user(document)

    async def get_by_id(self, user_id: str) -> User:
        object_id = _parse_object_id(user_id)
        document = await self._collection.find_one({"_id": object_id})
        if document is None:
            raise NotFoundError("User not found")
        return _document_to_user(document)

    async def list_users(self, skip: int, limit: int) -> list[User]:
        cursor = (
            self._collection.find({})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        return [_document_to_user(document) async for document in cursor]

    async def update(self, user_id: str, changes: UserChanges) -> User:
        if not changes.has_changes():
            return await self.get_by_id(user_id)

        object_id = _parse_object_id(user_id)
        updates: dict[str, Any] = {"updated_at": datetime.now(UTC)}
        if changes.email is not None:
            updates["email"] = changes.email
        if changes.full_name is not None:
            updates["full_name"] = changes.full_name
        if changes.phone is not None:
            updates["phone"] = changes.phone

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
        return _document_to_user(result)

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
