import asyncio
from datetime import UTC, datetime
from typing import Any, Protocol

from bson import ObjectId
from bson.errors import InvalidId

from app.core.memory import get_entitlements_store
from app.domain.entitlement import Entitlement, EntitlementStatus, Permission
from app.exceptions import ConflictError, NotFoundError
from app.schemas.entitlement import EntitlementCreate, EntitlementUpdate

_store_lock = asyncio.Lock()


class EntitlementRepository(Protocol):
    async def create(self, payload: EntitlementCreate) -> Entitlement: ...

    async def get_by_id(self, entitlement_id: str) -> Entitlement: ...

    async def list_entitlements(
        self,
        skip: int,
        limit: int,
        *,
        automation_key: str | None = None,
        ad_group: str | None = None,
        status: EntitlementStatus | None = None,
    ) -> list[Entitlement]: ...

    async def update(
        self, entitlement_id: str, payload: EntitlementUpdate
    ) -> Entitlement: ...

    async def delete(self, entitlement_id: str) -> None: ...


def _to_domain(document: dict[str, Any]) -> Entitlement:
    return Entitlement(
        id=str(document["_id"]),
        automation_key=document["automation_key"],
        ad_group=document["ad_group"],
        permissions=[Permission(item) for item in document["permissions"]],
        granted_by=document["granted_by"],
        granted_at=document["granted_at"],
        expires_at=document.get("expires_at"),
        status=EntitlementStatus(document["status"]),
        revoked_by=document.get("revoked_by"),
        revoked_at=document.get("revoked_at"),
        schema_version=document["schema_version"],
    )


def _parse_object_id(entitlement_id: str) -> str:
    try:
        return str(ObjectId(entitlement_id))
    except InvalidId:
        raise NotFoundError("Entitlement not found") from None


class InMemoryEntitlementRepository:
    """Grant-register persistence backed by a process-local dict."""

    def __init__(self) -> None:
        self._store = get_entitlements_store()

    def _unique_key(self, automation_key: str, ad_group: str) -> tuple[str, str]:
        return (automation_key.lower(), ad_group.lower())

    def _assert_unique(
        self,
        automation_key: str,
        ad_group: str,
        *,
        exclude_id: str | None = None,
    ) -> None:
        target = self._unique_key(automation_key, ad_group)
        for document_id, document in self._store.items():
            if exclude_id is not None and document_id == exclude_id:
                continue
            existing = self._unique_key(document["automation_key"], document["ad_group"])
            if existing == target:
                raise ConflictError(
                    "An entitlement already exists for this automation_key and ad_group"
                )

    async def create(self, payload: EntitlementCreate) -> Entitlement:
        async with _store_lock:
            self._assert_unique(payload.automation_key, payload.ad_group)
            now = datetime.now(UTC)
            object_id = str(ObjectId())
            document = {
                "_id": object_id,
                "automation_key": payload.automation_key,
                "ad_group": payload.ad_group,
                "permissions": [permission.value for permission in payload.permissions],
                "granted_by": payload.granted_by,
                "granted_at": now,
                "expires_at": payload.expires_at,
                "status": payload.status.value,
                "revoked_by": payload.revoked_by,
                "revoked_at": now if payload.status is EntitlementStatus.REVOKED else None,
                "schema_version": payload.schema_version,
            }
            self._store[object_id] = document
            return _to_domain(document)

    async def get_by_id(self, entitlement_id: str) -> Entitlement:
        object_id = _parse_object_id(entitlement_id)
        document = self._store.get(object_id)
        if document is None:
            raise NotFoundError("Entitlement not found")
        return _to_domain(document)

    async def list_entitlements(
        self,
        skip: int,
        limit: int,
        *,
        automation_key: str | None = None,
        ad_group: str | None = None,
        status: EntitlementStatus | None = None,
    ) -> list[Entitlement]:
        records = list(self._store.values())
        if automation_key is not None:
            records = [
                item
                for item in records
                if item["automation_key"].lower() == automation_key.lower()
            ]
        if ad_group is not None:
            records = [
                item for item in records if item["ad_group"].lower() == ad_group.lower()
            ]
        if status is not None:
            records = [item for item in records if item["status"] == status.value]
        records.sort(key=lambda item: item["granted_at"], reverse=True)
        return [_to_domain(item) for item in records[skip : skip + limit]]

    async def update(
        self, entitlement_id: str, payload: EntitlementUpdate
    ) -> Entitlement:
        object_id = _parse_object_id(entitlement_id)
        updates: dict[str, Any] = {}
        if payload.permissions is not None:
            updates["permissions"] = [
                permission.value for permission in payload.permissions
            ]
        if "expires_at" in payload.model_fields_set:
            updates["expires_at"] = payload.expires_at
        if payload.schema_version is not None:
            updates["schema_version"] = payload.schema_version

        async with _store_lock:
            document = self._store.get(object_id)
            if document is None:
                raise NotFoundError("Entitlement not found")

            current_status = EntitlementStatus(document["status"])
            if payload.status is not None:
                updates["status"] = payload.status.value
                if payload.status is EntitlementStatus.REVOKED:
                    updates["revoked_by"] = payload.revoked_by
                    updates["revoked_at"] = datetime.now(UTC)
                elif payload.status is EntitlementStatus.ACTIVE:
                    updates["revoked_by"] = None
                    updates["revoked_at"] = None
            elif payload.revoked_by is not None:
                if current_status is not EntitlementStatus.REVOKED:
                    raise ConflictError(
                        "revoked_by can only be set on a revoked entitlement"
                    )
                updates["revoked_by"] = payload.revoked_by

            document = {**document, **updates}
            self._store[object_id] = document
            return _to_domain(document)

    async def delete(self, entitlement_id: str) -> None:
        object_id = _parse_object_id(entitlement_id)
        async with _store_lock:
            if object_id not in self._store:
                raise NotFoundError("Entitlement not found")
            del self._store[object_id]
