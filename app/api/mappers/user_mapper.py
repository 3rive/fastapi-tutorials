from app.api.schemas.user import UserCreate, UserResponse, UserUpdate
from app.domain.user import NewUser, User, UserChanges


def to_new_user(payload: UserCreate) -> NewUser:
    return NewUser(
        email=str(payload.email).lower(),
        full_name=payload.full_name.strip(),
        phone=payload.phone,
    )


def to_user_changes(payload: UserUpdate) -> UserChanges:
    return UserChanges(
        email=str(payload.email).lower() if payload.email is not None else None,
        full_name=payload.full_name.strip() if payload.full_name is not None else None,
        phone=payload.phone,
    )


def to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
