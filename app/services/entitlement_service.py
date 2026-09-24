from datetime import UTC, datetime

from loguru import logger

from app.domain.entitlement import Entitlement, EntitlementStatus
from app.exceptions import BadRequestError
from app.repositories.entitlement_repository import EntitlementRepository
from app.schemas.entitlement import (
    EntitlementCreate,
    EntitlementResponse,
    EntitlementUpdate,
)


class EntitlementService:
    def __init__(self, repository: EntitlementRepository) -> None:
        self._repository = repository

    async def create_entitlement(self, payload: EntitlementCreate) -> EntitlementResponse:
        logger.info(
            "Creating entitlement automation_key={} ad_group={}",
            payload.automation_key,
            payload.ad_group,
        )
        self._assert_expiry(payload.expires_at, datetime.now(UTC))
        entitlement = await self._repository.create(payload)
        return _to_response(entitlement)

    async def get_entitlement(self, entitlement_id: str) -> EntitlementResponse:
        entitlement = await self._repository.get_by_id(entitlement_id)
        return _to_response(entitlement)

    async def list_entitlements(
        self,
        skip: int,
        limit: int,
        *,
        automation_key: str | None = None,
        ad_group: str | None = None,
        status: EntitlementStatus | None = None,
    ) -> list[EntitlementResponse]:
        entitlements = await self._repository.list_entitlements(
            skip=skip,
            limit=limit,
            automation_key=automation_key,
            ad_group=ad_group,
            status=status,
        )
        return [_to_response(item) for item in entitlements]

    async def update_entitlement(
        self,
        entitlement_id: str,
        payload: EntitlementUpdate,
    ) -> EntitlementResponse:
        logger.info("Updating entitlement id={}", entitlement_id)
        current = await self._repository.get_by_id(entitlement_id)
        expires_at = (
            payload.expires_at
            if "expires_at" in payload.model_fields_set
            else current.expires_at
        )
        self._assert_expiry(expires_at, current.granted_at)
        entitlement = await self._repository.update(entitlement_id, payload)
        return _to_response(entitlement)

    async def delete_entitlement(self, entitlement_id: str) -> None:
        logger.info("Deleting entitlement id={}", entitlement_id)
        await self._repository.delete(entitlement_id)

    def _assert_expiry(self, expires_at: datetime | None, granted_at: datetime) -> None:
        if expires_at is None:
            return
        expiry = expires_at if expires_at.tzinfo else expires_at.replace(tzinfo=UTC)
        granted = granted_at if granted_at.tzinfo else granted_at.replace(tzinfo=UTC)
        if expiry <= granted:
            raise BadRequestError("expires_at must be later than granted_at")


def _to_response(entitlement: Entitlement) -> EntitlementResponse:
    return EntitlementResponse.model_validate(entitlement)
