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
