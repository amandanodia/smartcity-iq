"""Configuration. Secrets come from environment variables only."""
import os
from typing import Mapping, Optional


def normalize_database_url(url: Optional[str]) -> str:
    """Hosted providers often issue ``postgres://`` URLs; SQLAlchemy needs ``postgresql://``."""
    if not url:
        return ""
    url = url.strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return url


def load_config(env: Optional[Mapping[str, str]] = None) -> dict:
    env = os.environ if env is None else env
    return {
        "DATABASE_URL": normalize_database_url(env.get("DATABASE_URL")),
        "SECRET_KEY": env.get("SECRET_KEY", ""),
    }
