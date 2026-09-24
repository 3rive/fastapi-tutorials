from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_entitlement_service
from app.domain.entitlement import EntitlementStatus
from app.schemas.entitlement import (
    EntitlementCreate,
    EntitlementResponse,
    EntitlementUpdate,
)
from app.services.entitlement_service import EntitlementService

router = APIRouter(prefix="/entitlements", tags=["entitlements"])


@router.post("", response_model=EntitlementResponse, status_code=status.HTTP_201_CREATED)
async def create_entitlement(
    payload: EntitlementCreate,
    service: Annotated[EntitlementService, Depends(get_entitlement_service)],
) -> EntitlementResponse:
    return await service.create_entitlement(payload)


@router.get("", response_model=list[EntitlementResponse])
async def list_entitlements(
    service: Annotated[EntitlementService, Depends(get_entitlement_service)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    automation_key: Annotated[str | None, Query(min_length=1)] = None,
    ad_group: Annotated[str | None, Query(min_length=1)] = None,
    entitlement_status: Annotated[
        EntitlementStatus | None,
        Query(alias="status"),
    ] = None,
) -> list[EntitlementResponse]:
    return await service.list_entitlements(
        skip=skip,
        limit=limit,
        automation_key=automation_key,
        ad_group=ad_group,
        status=entitlement_status,
    )


@router.get("/{entitlement_id}", response_model=EntitlementResponse)
async def get_entitlement(
    entitlement_id: str,
    service: Annotated[EntitlementService, Depends(get_entitlement_service)],
) -> EntitlementResponse:
    return await service.get_entitlement(entitlement_id)


@router.patch("/{entitlement_id}", response_model=EntitlementResponse)
async def update_entitlement(
    entitlement_id: str,
    payload: EntitlementUpdate,
    service: Annotated[EntitlementService, Depends(get_entitlement_service)],
) -> EntitlementResponse:
    return await service.update_entitlement(entitlement_id, payload)


@router.delete("/{entitlement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entitlement(
    entitlement_id: str,
    service: Annotated[EntitlementService, Depends(get_entitlement_service)],
) -> None:
    await service.delete_entitlement(entitlement_id)
