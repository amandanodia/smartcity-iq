"""Create all tables directly from the models (development convenience).

For tracked schema changes use Alembic instead: see README, "Database setup".
"""
from dotenv import load_dotenv

from app import db
from app.config import load_config
from app.models import Base


def main() -> None:
    load_dotenv()
    engine = db.init_db(load_config()["DATABASE_URL"])
    Base.metadata.create_all(engine)
    print("Tables ready:", ", ".join(sorted(Base.metadata.tables)))


if __name__ == "__main__":
    main()
