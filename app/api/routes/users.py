from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_user_service
from app.api.mappers.user_mapper import to_new_user, to_user_changes, to_user_response
from app.api.schemas.user import UserCreate, UserResponse, UserUpdate
from app.application.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = await service.create_user(to_new_user(payload))
    return to_user_response(user)


@router.get("", response_model=list[UserResponse])
async def list_users(
    service: Annotated[UserService, Depends(get_user_service)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[UserResponse]:
    users = await service.list_users(skip=skip, limit=limit)
    return [to_user_response(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = await service.get_user(user_id)
    return to_user_response(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = await service.update_user(user_id, to_user_changes(payload))
    return to_user_response(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    await service.delete_user(user_id)
