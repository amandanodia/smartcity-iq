"""Reference tables: cities, aliases, sources, datasets and stations."""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean, CheckConstraint, Date, DateTime, Float, ForeignKey, String, Text, UniqueConstraint,
    false, true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    AccessMethod, Base, DataClass, Domain, GeoLevel, TimestampMixin, enum_check,
)


class City(TimestampMixin, Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    state: Mapped[str] = mapped_column(String(120), nullable=False)
    country: Mapped[str] = mapped_column(String(60), nullable=False, default="India", server_default="India")
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())

    aliases: Mapped[list["CityAlias"]] = relationship(
        back_populates="city", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("name", "state", name="uq_cities_name_state"),
        CheckConstraint("latitude IS NULL OR latitude BETWEEN 6 AND 38", name="latitude_in_india"),
        CheckConstraint("longitude IS NULL OR longitude BETWEEN 68 AND 98", name="longitude_in_india"),
    )


class CityAlias(TimestampMixin, Base):
    __tablename__ = "city_aliases"

    id: Mapped[int] = mapped_column(primary_key=True)
    city_id: Mapped[int] = mapped_column(
        ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    alias: Mapped[str] = mapped_column(String(120), nullable=False)
    alias_normalized: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    city: Mapped["City"] = relationship(back_populates="aliases")


class DataSource(TimestampMixin, Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    base_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    access_method: Mapped[str] = mapped_column(String(20), nullable=False)
    licence: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    terms_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    rate_limit_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Name of the environment variable holding the key. Never the key itself.
    api_key_env_var: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    datasets: Mapped[list["Dataset"]] = relationship(back_populates="source")

    __table_args__ = (enum_check("access_method", AccessMethod),)


class Dataset(TimestampMixin, Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("data_sources.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(40), nullable=False, default="1", server_default="1")
    domain: Mapped[str] = mapped_column(String(30), nullable=False)
    geo_level: Mapped[str] = mapped_column(String(20), nullable=False)
    data_class: Mapped[str] = mapped_column(String(20), nullable=False)
    coverage_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unit_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    original_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    licence: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    observation_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    observation_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_imported_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    source: Mapped["DataSource"] = relationship(back_populates="datasets")

    __table_args__ = (
        UniqueConstraint("source_id", "name", "version", name="uq_datasets_source_name_version"),
        enum_check("domain", Domain),
        enum_check("geo_level", GeoLevel),
        enum_check("data_class", DataClass),
        CheckConstraint(
            "observation_end IS NULL OR observation_start IS NULL OR observation_end >= observation_start",
            name="observation_period_order",
        ),
    )


class Station(TimestampMixin, Base):
    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("data_sources.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    city_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("cities.id", ondelete="SET NULL"), nullable=True, index=True
    )
    external_id: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # Raw coordinates are kept even when invalid; coords_valid records the validation outcome.
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    coords_valid: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    coords_note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    __table_args__ = (UniqueConstraint("source_id", "external_id", name="uq_stations_source_external"),)
