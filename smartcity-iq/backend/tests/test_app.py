import pytest

from app import create_app


def test_health_reports_database_up():
    flask_app = create_app({"DATABASE_URL": "sqlite://", "TESTING": True})
    resp = flask_app.test_client().get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok", "database": "up"}


def test_missing_database_url_fails_loudly():
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        create_app({"DATABASE_URL": ""})
