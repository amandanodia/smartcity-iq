from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.models import Base, City, DataSource, Dataset


@pytest.fixture()
def engine():
    eng = create_engine("sqlite://")

    @event.listens_for(eng, "connect")
    def _foreign_keys_on(dbapi_conn, _record):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def session(engine):
    with Session(engine) as s:
        yield s


@pytest.fixture()
def ctx(session):
    """A city, a source and a dataset that fact rows can point at."""
    city = City(slug="jaipur", name="Jaipur", state="Rajasthan")
    source = DataSource(name="Test source", access_method="csv")
    session.add_all([city, source])
    session.flush()
    dataset = Dataset(
        source_id=source.id, name="Test dataset", domain="air_quality",
        geo_level="station", data_class="sample",
    )
    session.add(dataset)
    session.commit()
    return SimpleNamespace(city=city, source=source, dataset=dataset)
