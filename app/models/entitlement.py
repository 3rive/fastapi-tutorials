from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import UTCDateTime, Base


class EntitlementRow(Base):
    __tablename__ = "entitlements"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    automation_key: Mapped[str] = mapped_column(String(200), nullable=False)
    ad_group: Mapped[str] = mapped_column(String(200), nullable=False)
    permissions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    granted_by: Mapped[str] = mapped_column(String(200), nullable=False)
    granted_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    revoked_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        Index(
            "uq_entitlements_automation_ad_group",
            func.lower(automation_key),
            func.lower(ad_group),
            unique=True,
        ),
    )
