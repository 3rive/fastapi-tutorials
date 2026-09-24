from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entitlement import Entitlement, EntitlementStatus, Permission
from app.exceptions import ConflictError, NotFoundError
from app.models.entitlement import EntitlementRow
from app.schemas.entitlement import EntitlementCreate, EntitlementUpdate


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


def _to_domain(row: EntitlementRow) -> Entitlement:
    return Entitlement(
        id=row.id,
        automation_key=row.automation_key,
        ad_group=row.ad_group,
        permissions=[Permission(item) for item in row.permissions],
        granted_by=row.granted_by,
        granted_at=row.granted_at,
        expires_at=row.expires_at,
        status=EntitlementStatus(row.status),
        revoked_by=row.revoked_by,
        revoked_at=row.revoked_at,
        schema_version=row.schema_version,
    )


class SqliteEntitlementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, payload: EntitlementCreate) -> Entitlement:
        now = datetime.now(UTC)
        row = EntitlementRow(
            automation_key=payload.automation_key,
            ad_group=payload.ad_group,
            permissions=[permission.value for permission in payload.permissions],
            granted_by=payload.granted_by,
            granted_at=now,
            expires_at=payload.expires_at,
            status=payload.status.value,
            revoked_by=payload.revoked_by,
            revoked_at=now if payload.status is EntitlementStatus.REVOKED else None,
            schema_version=payload.schema_version,
        )
        self._session.add(row)
        try:
            await self._session.flush()
        except IntegrityError:
            raise ConflictError(
                "An entitlement already exists for this automation_key and ad_group"
            ) from None
        return _to_domain(row)

    async def get_by_id(self, entitlement_id: str) -> Entitlement:
        row = await self._session.get(EntitlementRow, entitlement_id)
        if row is None:
            raise NotFoundError("Entitlement not found")
        return _to_domain(row)

    async def list_entitlements(
        self,
        skip: int,
        limit: int,
        *,
        automation_key: str | None = None,
        ad_group: str | None = None,
        status: EntitlementStatus | None = None,
    ) -> list[Entitlement]:
        stmt = select(EntitlementRow)
        if automation_key is not None:
            stmt = stmt.where(
                func.lower(EntitlementRow.automation_key) == automation_key.lower()
            )
        if ad_group is not None:
            stmt = stmt.where(func.lower(EntitlementRow.ad_group) == ad_group.lower())
        if status is not None:
            stmt = stmt.where(EntitlementRow.status == status.value)
        stmt = (
            stmt.order_by(EntitlementRow.granted_at.desc()).offset(skip).limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_to_domain(row) for row in result.scalars().all()]

    async def update(
        self, entitlement_id: str, payload: EntitlementUpdate
    ) -> Entitlement:
        row = await self._session.get(EntitlementRow, entitlement_id)
        if row is None:
            raise NotFoundError("Entitlement not found")

        if payload.permissions is not None:
            row.permissions = [permission.value for permission in payload.permissions]
        if "expires_at" in payload.model_fields_set:
            row.expires_at = payload.expires_at
        if payload.schema_version is not None:
            row.schema_version = payload.schema_version

        current_status = EntitlementStatus(row.status)
        if payload.status is not None:
            row.status = payload.status.value
            if payload.status is EntitlementStatus.REVOKED:
                row.revoked_by = payload.revoked_by
                row.revoked_at = datetime.now(UTC)
            elif payload.status is EntitlementStatus.ACTIVE:
                row.revoked_by = None
                row.revoked_at = None
        elif payload.revoked_by is not None:
            if current_status is not EntitlementStatus.REVOKED:
                raise ConflictError(
                    "revoked_by can only be set on a revoked entitlement"
                )
            row.revoked_by = payload.revoked_by

        try:
            await self._session.flush()
        except IntegrityError:
            raise ConflictError(
                "An entitlement already exists for this automation_key and ad_group"
            ) from None
        return _to_domain(row)

    async def delete(self, entitlement_id: str) -> None:
        row = await self._session.get(EntitlementRow, entitlement_id)
        if row is None:
            raise NotFoundError("Entitlement not found")
        await self._session.delete(row)
        await self._session.flush()
