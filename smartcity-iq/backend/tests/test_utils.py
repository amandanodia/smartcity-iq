from datetime import date, datetime, timedelta, timezone

import pytest

from app.config import load_config, normalize_database_url
from app.utils.keys import make_record_key
from app.utils.names import normalize_name


def test_record_key_is_stable_and_64_hex_chars():
    k = make_record_key("air_quality", 1, "pm25", date(2026, 1, 1))
    assert k == make_record_key("air_quality", 1, "pm25", date(2026, 1, 1))
    assert len(k) == 64 and int(k, 16) >= 0


def test_record_key_distinguishes_none_from_empty_string():
    assert make_record_key("t", None) != make_record_key("t", "")


def test_record_key_treats_nan_as_missing():
    assert make_record_key("t", float("nan")) == make_record_key("t", None)


def test_record_key_depends_on_order_and_content():
    assert make_record_key("t", "a", "b") != make_record_key("t", "b", "a")
    assert make_record_key("t", 1) != make_record_key("t", 2)


def test_record_key_same_instant_in_different_timezones_matches():
    utc = datetime(2026, 1, 1, 6, 0, tzinfo=timezone.utc)
    ist = utc.astimezone(timezone(timedelta(hours=5, minutes=30)))
    assert make_record_key("t", utc) == make_record_key("t", ist)


def test_record_key_rejects_naive_datetime():
    with pytest.raises(ValueError):
        make_record_key("t", datetime(2026, 1, 1))


def test_normalize_name():
    assert normalize_name("  Bengaluru ") == "bengaluru"
    assert normalize_name("Navi-Mumbai.") == "navi mumbai"
    assert normalize_name("NEW   DELHI") == "new delhi"
    assert normalize_name(None) == ""


def test_postgres_url_is_normalised():
    assert normalize_database_url("postgres://u:p@h/db") == "postgresql://u:p@h/db"
    assert normalize_database_url("postgresql://u:p@h/db") == "postgresql://u:p@h/db"
    assert normalize_database_url(None) == ""


def test_load_config_reads_given_env_only():
    cfg = load_config({"DATABASE_URL": "postgres://x/y", "SECRET_KEY": "s"})
    assert cfg == {"DATABASE_URL": "postgresql://x/y", "SECRET_KEY": "s"}
