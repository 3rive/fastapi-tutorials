from datetime import datetime
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.domain.entitlement import EntitlementStatus, Permission

NonEmptyStr = Annotated[str, Field(min_length=1, max_length=200)]
PermissionList = Annotated[list[Permission], Field(min_length=1)]


def _dedupe_permissions(values: list[Permission]) -> list[Permission]:
    seen: set[Permission] = set()
    unique: list[Permission] = []
    for permission in values:
        if permission not in seen:
            seen.add(permission)
            unique.append(permission)
    return unique


class EntitlementCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    automation_key: NonEmptyStr
    ad_group: NonEmptyStr
    permissions: PermissionList
    granted_by: NonEmptyStr
    expires_at: datetime | None = None
    status: EntitlementStatus = EntitlementStatus.ACTIVE
    revoked_by: str | None = None
    schema_version: Annotated[int, Field(ge=1)] = 1

    @field_validator("automation_key", "ad_group", "granted_by", "revoked_by")
    @classmethod
    def strip_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("permissions")
    @classmethod
    def unique_permissions(cls, value: list[Permission]) -> list[Permission]:
        return _dedupe_permissions(value)

    @model_validator(mode="after")
    def validate_grant_state(self) -> Self:
        if self.status is EntitlementStatus.REVOKED and not self.revoked_by:
            raise ValueError("revoked_by is required when status is revoked")
        if self.status is EntitlementStatus.ACTIVE and self.revoked_by:
            raise ValueError("revoked_by must be omitted when status is active")
        return self


class EntitlementUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    permissions: PermissionList | None = None
    expires_at: datetime | None = None
    status: EntitlementStatus | None = None
    revoked_by: str | None = None
    schema_version: Annotated[int, Field(ge=1)] | None = None

    @field_validator("revoked_by")
    @classmethod
    def strip_revoked_by(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("permissions")
    @classmethod
    def unique_permissions(
        cls, value: list[Permission] | None
    ) -> list[Permission] | None:
        if value is None:
            return None
        return _dedupe_permissions(value)

    @model_validator(mode="after")
    def validate_revoke_payload(self) -> Self:
        if self.status is EntitlementStatus.REVOKED and not self.revoked_by:
            raise ValueError("revoked_by is required when status is revoked")
        if self.status is EntitlementStatus.ACTIVE and self.revoked_by:
            raise ValueError("revoked_by must be omitted when status is active")
        return self


class EntitlementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    automation_key: str
    ad_group: str
    permissions: list[Permission]
    granted_by: str
    granted_at: datetime
    expires_at: datetime | None
    status: EntitlementStatus
    revoked_by: str | None
    revoked_at: datetime | None
    schema_version: int
