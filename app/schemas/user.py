from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    full_name: Annotated[str, Field(min_length=1, max_length=200)]
    phone: Annotated[str | None, Field(max_length=32)] = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: Annotated[str | None, Field(min_length=1, max_length=200)] = None
    phone: Annotated[str | None, Field(max_length=32)] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    full_name: str
    phone: str | None
    created_at: datetime
    updated_at: datetime
