from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Permission(StrEnum):
    VIEW = "view"
    EXECUTE = "execute"


class EntitlementStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"


@dataclass(slots=True)
class Entitlement:
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
