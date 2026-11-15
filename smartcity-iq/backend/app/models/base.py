"""Declarative base, shared column mixins and controlled vocabularies."""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, JSON, MetaData, String, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# JSONB on PostgreSQL, plain JSON elsewhere (keeps tests runnable on SQLite).
JSONType = JSON().with_variant(JSONB(), "postgresql")
# BIGINT primary keys on PostgreSQL; INTEGER on SQLite so autoincrement works in tests.
BigIntPK = BigInteger().with_variant(Integer(), "sqlite")


class DataClass(str, enum.Enum):
    REAL_TIME = "real_time"
    HISTORICAL = "historical"
    MANUAL_IMPORT = "manual_import"
    SAMPLE = "sample"


class GeoLevel(str, enum.Enum):
    STATION = "station"
    CITY = "city"
    DISTRICT = "district"
    STATE = "state"
    NATIONAL = "national"


class AccessMethod(str, enum.Enum):
    API = "api"
    CSV = "csv"
    MANUAL = "manual"


class Domain(str, enum.Enum):
    AIR_QUALITY = "air_quality"
    TRAFFIC = "traffic"
    ROAD_SAFETY = "road_safety"
    WATER = "water"
    POPULATION = "population"
    INFRASTRUCTURE = "infrastructure"


class Pollutant(str, enum.Enum):
    PM25 = "pm25"
    PM10 = "pm10"
    NO2 = "no2"
    SO2 = "so2"
    CO = "co"
    O3 = "o3"
    AQI = "aqi"


class AccidentCategory(str, enum.Enum):
    TOTAL = "total"
    COLLISION_TYPE = "collision_type"
    VIOLATION_TYPE = "violation_type"
    LICENSE_TYPE = "license_type"
    ROAD_USER = "road_user"
    ROAD_CATEGORY = "road_category"
    SAFETY_DEVICE = "safety_device"


class RunStatus(str, enum.Enum):
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


def enum_check(column: str, enum_cls: type) -> CheckConstraint:
    values = ", ".join(f"'{m.value}'" for m in enum_cls)
    return CheckConstraint(f"{column} IN ({values})", name=f"{column}_valid")


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class FactMixin(TimestampMixin):
    """Columns every fact table shares: dedupe key, provenance and data class."""

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    record_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    data_class: Mapped[str] = mapped_column(String(20), nullable=False)
    raw_ref: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)

    @declared_attr
    def dataset_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey("datasets.id", ondelete="RESTRICT"), nullable=False, index=True
        )

    @declared_attr
    def batch_id(cls) -> Mapped[Optional[int]]:
        return mapped_column(
            ForeignKey("import_batches.id", ondelete="SET NULL"), nullable=True, index=True
        )
