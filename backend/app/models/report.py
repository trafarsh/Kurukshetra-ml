"""Engineering reports model."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.session import Session


class Report(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "reports"

    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)  # SESSION_DEBRIEF, CALIBRATION_AUDIT, etc.
    file_path_pdf: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path_csv: Mapped[str] = mapped_column(String(500), nullable=False)
    summary_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    session: Mapped["Session"] = relationship(back_populates="reports")

