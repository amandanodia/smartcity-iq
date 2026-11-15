from sqlalchemy import func, select

from app.models import City, CityAlias, DataSource
from scripts.seed_reference import seed_reference


def test_seed_creates_eight_cities_and_sources(session):
    result = seed_reference(session)
    session.commit()
    assert result["cities"] == 8
    assert session.scalar(select(func.count()).select_from(City)) == 8
    assert session.scalar(select(func.count()).select_from(DataSource)) == 8


def test_seed_is_idempotent(session):
    seed_reference(session)
    session.commit()
    again = seed_reference(session)
    session.commit()
    assert again == {"cities": 0, "aliases": 0, "sources": 0}


def test_alias_lookup_resolves_old_names(session):
    seed_reference(session)
    session.commit()
    for alias, slug in [("bangalore", "bengaluru"), ("bombay", "mumbai"), ("madras", "chennai")]:
        city = session.scalar(
            select(City).join(CityAlias).where(CityAlias.alias_normalized == alias)
        )
        assert city.slug == slug


def test_seed_stores_no_secrets(session):
    seed_reference(session)
    session.commit()
    for src in session.scalars(select(DataSource)):
        # api_key_env_var holds a variable NAME, never a key value
        assert src.api_key_env_var is None or src.api_key_env_var.isupper()
