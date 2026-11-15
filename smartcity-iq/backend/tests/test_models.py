from datetime import date, datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import (
    AirQuality, Base, City, CityAlias, Dataset, ImportBatch, RoadAccident, TrafficStatistic,
)

EXPECTED_TABLES = {
    "cities", "city_aliases", "data_sources", "datasets", "stations", "air_quality",
    "traffic_statistics", "road_accidents", "water_statistics", "population_statistics",
    "infrastructure", "import_batches", "data_refresh_logs",
}
NOW = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)


def assert_rejected(session, *objs):
    session.add_all(objs)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def aq(ctx, key="k1", **over):
    fields = dict(
        record_key=key, dataset_id=ctx.dataset.id, city_id=ctx.city.id, parameter="pm25",
        value=40.0, unit="ug/m3", observed_at=NOW, data_class="sample",
    )
    fields.update(over)
    return AirQuality(**fields)


def test_expected_tables_exist():
    assert set(Base.metadata.tables) == EXPECTED_TABLES


def test_valid_air_quality_row_saves_with_timestamps(session, ctx):
    row = aq(ctx)
    session.add(row)
    session.commit()
    assert row.id is not None and row.created_at is not None


def test_duplicate_record_key_rejected(session, ctx):
    session.add(aq(ctx, "dup"))
    session.commit()
    assert_rejected(session, aq(ctx, "dup"))


def test_invalid_data_class_rejected(session, ctx):
    assert_rejected(session, aq(ctx, data_class="live"))


def test_invalid_pollutant_rejected(session, ctx):
    assert_rejected(session, aq(ctx, parameter="pm1"))


def test_missing_value_must_be_explicit(session, ctx):
    assert_rejected(session, aq(ctx, "m1", value=None, unit=None))
    session.add(aq(ctx, "m2", value=None, unit=None, is_missing=True))
    session.commit()


def test_value_requires_unit(session, ctx):
    assert_rejected(session, aq(ctx, unit=None))


def test_foreign_key_enforced(session, ctx):
    assert_rejected(session, aq(ctx, city_id=9999))


def test_city_level_accident_needs_city(session, ctx):
    base = dict(dataset_id=ctx.dataset.id, year=2024, accidents=10, data_class="historical")
    assert_rejected(session, RoadAccident(record_key="a1", geo_level="city", **base))
    session.add(RoadAccident(record_key="a2", geo_level="city", city_id=ctx.city.id, **base))
    session.commit()


def test_state_level_accident_needs_state_name(session, ctx):
    base = dict(dataset_id=ctx.dataset.id, year=2024, accidents=10, data_class="historical")
    assert_rejected(session, RoadAccident(record_key="s1", geo_level="state", **base))
    session.add(RoadAccident(record_key="s2", geo_level="state", state_name="Rajasthan", **base))
    session.commit()


def test_negative_accident_counts_rejected(session, ctx):
    assert_rejected(session, RoadAccident(
        record_key="n1", dataset_id=ctx.dataset.id, geo_level="state", state_name="X",
        year=2024, fatalities=-1, data_class="historical"))


def test_traffic_period_must_not_end_before_start(session, ctx):
    assert_rejected(session, TrafficStatistic(
        record_key="t1", dataset_id=ctx.dataset.id, city_id=ctx.city.id, metric="volume",
        value=1.0, unit="vehicles", period_start=date(2025, 2, 1), period_end=date(2025, 1, 1),
        data_class="sample"))


def test_dataset_unique_per_source_name_version(session, ctx):
    assert_rejected(session, Dataset(
        source_id=ctx.source.id, name="Test dataset", domain="air_quality",
        geo_level="station", data_class="sample"))


def test_alias_normalized_is_unique(session, ctx):
    session.add(CityAlias(city_id=ctx.city.id, alias="Jaipur", alias_normalized="jaipur"))
    session.commit()
    assert_rejected(session, CityAlias(city_id=ctx.city.id, alias="JAIPUR", alias_normalized="jaipur"))


def test_city_coordinates_must_be_in_india(session):
    assert_rejected(session, City(slug="x", name="X", state="Y", latitude=51.5, longitude=-0.1))


def test_same_file_cannot_be_imported_twice_for_a_dataset(session, ctx):
    session.add(ImportBatch(dataset_id=ctx.dataset.id, file_checksum="abc"))
    session.commit()
    assert_rejected(session, ImportBatch(dataset_id=ctx.dataset.id, file_checksum="abc"))


def test_api_batches_without_checksum_are_allowed(session, ctx):
    session.add_all([ImportBatch(dataset_id=ctx.dataset.id), ImportBatch(dataset_id=ctx.dataset.id)])
    session.commit()
