"""Fact tables. Missing values are stored explicitly, never imputed."""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, Date, DateTime, Float, ForeignKey, Index, Integer,
    String, false,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import (
    AccidentCategory, Base, DataClass, FactMixin, GeoLevel, JSONType, Pollutant, enum_check,
)


def _measure_checks() -> tuple:
    """Rules for tables that store one numeric measurement per row."""
    return (
        CheckConstraint("is_missing OR value IS NOT NULL", name="value_or_missing"),
        CheckConstraint("value IS NULL OR unit IS NOT NULL", name="unit_required_with_value"),
        enum_check("data_class", DataClass),
        enum_check("geo_level", GeoLevel),
    )


class AirQuality(FactMixin, Base):
    __tablename__ = "air_quality"

    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"), nullable=False)
    station_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("stations.id", ondelete="RESTRICT"), nullable=True
    )
    geo_level: Mapped[str] = mapped_column(String(20), nullable=False, default="station", server_default="station")
    parameter: Mapped[str] = mapped_column(String(10), nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_missing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    unit: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    original_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    original_unit: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("ix_air_quality_city_param_time", "city_id", "parameter", "observed_at"),
        Index("ix_air_quality_station_time", "station_id", "observed_at"),
        enum_check("parameter", Pollutant),
        *_measure_checks(),
    )


class TrafficStatistic(FactMixin, Base):
    __tablename__ = "traffic_statistics"

    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"), nullable=False)
    geo_level: Mapped[str] = mapped_column(String(20), nullable=False, default="city", server_default="city")
    metric: Mapped[str] = mapped_column(String(60), nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_missing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    unit: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    original_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    original_unit: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        Index("ix_traffic_city_metric_period", "city_id", "metric", "period_start"),
        CheckConstraint("period_end >= period_start", name="period_order"),
        *_measure_checks(),
    )


class WaterStatistic(FactMixin, Base):
    __tablename__ = "water_statistics"

    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"), nullable=False)
    geo_level: Mapped[str] = mapped_column(String(20), nullable=False, default="city", server_default="city")
    metric: Mapped[str] = mapped_column(String(60), nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_missing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    unit: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    original_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    original_unit: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        Index("ix_water_city_metric_period", "city_id", "metric", "period_start"),
        CheckConstraint("period_end >= period_start", name="period_order"),
        *_measure_checks(),
    )


class RoadAccident(FactMixin, Base):
    __tablename__ = "road_accidents"

    city_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"), nullable=True)
    state_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    geo_level: Mapped[str] = mapped_column(String(20), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    category_type: Mapped[str] = mapped_column(String(30), nullable=False, default="total", server_default="total")
    category_value: Mapped[str] = mapped_column(String(120), nullable=False, default="total", server_default="total")
    accidents: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fatalities: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    injuries: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_road_accidents_city_year", "city_id", "year"),
        Index("ix_road_accidents_state_year", "state_name", "year"),
        Index("ix_road_accidents_category_year", "category_type", "year"),
        enum_check("category_type", AccidentCategory),
        enum_check("data_class", DataClass),
        enum_check("geo_level", GeoLevel),
        CheckConstraint("geo_level <> 'city' OR city_id IS NOT NULL", name="city_required_for_city_level"),
        CheckConstraint("geo_level <> 'state' OR state_name IS NOT NULL", name="state_required_for_state_level"),
        CheckConstraint("year BETWEEN 1900 AND 2100", name="year_plausible"),
        CheckConstraint(
            "(accidents IS NULL OR accidents >= 0) AND (fatalities IS NULL OR fatalities >= 0) "
            "AND (injuries IS NULL OR injuries >= 0)",
            name="counts_non_negative",
        ),
    )


class PopulationStatistic(FactMixin, Base):
    __tablename__ = "population_statistics"

    city_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"), nullable=True)
    state_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    district_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    geo_level: Mapped[str] = mapped_column(String(20), nullable=False)
    census_year: Mapped[int] = mapped_column(Integer, nullable=False)
    population: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    households: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    area_sq_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    extra: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)

    __table_args__ = (
        Index("ix_population_city_year", "city_id", "census_year"),
        enum_check("data_class", DataClass),
        enum_check("geo_level", GeoLevel),
        CheckConstraint("geo_level <> 'city' OR city_id IS NOT NULL", name="city_required_for_city_level"),
        CheckConstraint("census_year BETWEEN 1800 AND 2100", name="year_plausible"),
        CheckConstraint(
            "(population IS NULL OR population >= 0) AND (households IS NULL OR households >= 0)",
            name="counts_non_negative",
        ),
    )


class Infrastructure(FactMixin, Base):
    __tablename__ = "infrastructure"

    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"), nullable=False)
    facility_type: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    coords_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    ward_zone: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    properties: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)

    __table_args__ = (
        Index("ix_infrastructure_city_type", "city_id", "facility_type"),
        enum_check("data_class", DataClass),
    )
