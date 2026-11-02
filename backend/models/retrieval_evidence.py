from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base


class RetrievalEvidence(Base):
    __tablename__ = "retrieval_evidence"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    message_id: Mapped[int] = mapped_column(
        ForeignKey("conversation_messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    medical_record_id: Mapped[int | None] = mapped_column(
        ForeignKey("medical_records.id", ondelete="SET NULL"),
        nullable=True
    )

    source_reference: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    source: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    page: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    distance: Mapped[float] = mapped_column(
        nullable=False
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )