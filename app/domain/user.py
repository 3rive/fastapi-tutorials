from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class User:
    id: str
    email: str
    full_name: str
    phone: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True, frozen=True)
class NewUser:
    email: str
    full_name: str
    phone: str | None = None


@dataclass(slots=True)
class UserChanges:
    email: str | None = None
    full_name: str | None = None
    phone: str | None = None

    def has_changes(self) -> bool:
        return any(
            value is not None
            for value in (self.email, self.full_name, self.phone)
        )
