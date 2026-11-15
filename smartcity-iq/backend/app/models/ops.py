"""Import bookkeeping: one batch per import, one log row per refresh run."""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, JSONType, RunStatus, TimestampMixin, enum_check


class ImportBatch(TimestampMixin, Base):
    __tablename__ = "import_batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # SHA-256 of the imported file. NULL for API pulls, which have no file.
    file_checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    raw_ref: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    rows_read: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    rows_loaded: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    rows_rejected: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    rows_duplicate: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    __table_args__ = (
        UniqueConstraint("dataset_id", "file_checksum", name="uq_import_batches_dataset_checksum"),
    )


class DataRefreshLog(TimestampMixin, Base):
    __tablename__ = "data_refresh_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id", ondelete="RESTRICT"), nullable=False)
    batch_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("import_batches.id", ondelete="SET NULL"), nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rows_missing_values: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_data_refresh_logs_dataset_started", "dataset_id", "started_at"),
        enum_check("status", RunStatus),
        CheckConstraint("finished_at IS NULL OR finished_at >= started_at", name="finish_after_start"),
    )
