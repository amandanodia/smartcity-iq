# SmartCity IQ: Indian Urban Intelligence Platform

Interactive maps, charts and comparisons of urban datasets for Jaipur, Delhi, Mumbai, Bengaluru,
Hyderabad, Chennai, Pune and Ahmedabad. Built as a portfolio project for the Tata Forage Data
Visualisation certification.

**Status: Phase 2 of 8 (project structure and database).** The frontend, connectors and analytics are
not built yet. Nothing here displays real measurements.

## Data integrity rules
- No measurement is fabricated or imputed. Missing values are stored as `NULL` with `is_missing = true`.
- Every fact row carries a `data_class`: `real_time`, `historical`, `manual_import` or `sample`.
- Every dataset records its source, licence, geographic level, coverage and import date.
- API keys live in environment variables only (see `.env.example`).

## Layout
```
backend/   Flask app, SQLAlchemy models, Alembic migrations, scripts, tests
frontend/  React + TypeScript app (Phase 5)
docs/      Architecture and, later, API and data source documentation
data/      Sample files, clearly labelled as sample data
```

## Database setup (cloud or local)
Requires Python 3.12+ and a PostgreSQL database (any hosted provider works).

```bash
cd backend
pip install -r ../requirements-dev.txt
cp ../.env.example .env            # then set DATABASE_URL
alembic revision --autogenerate -m "initial schema"   # first time only; review the file it writes
alembic upgrade head
python -m scripts.seed_reference   # 8 cities, aliases, data source registry (safe to re-run)
pytest
flask --app app:create_app run     # GET /api/health
```
For a quick throwaway setup without Alembic: `python -m scripts.init_db`.

## Licence and attribution
Each data source keeps its own licence; see the `data_sources` table and `docs/` (Phase 8).
