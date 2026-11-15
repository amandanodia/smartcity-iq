"""Seed reference data: the 8 launch cities, their aliases, and the data-source registry.

Idempotent: existing rows are left untouched, so manual edits are never overwritten.
No measurements are created here. Licence fields that have not been verified say so.
"""
from sqlalchemy import select

from app.models import AccessMethod, City, CityAlias, DataSource
from app.utils.names import normalize_name

# City centroids are reference geography (not measurements).
CITIES = [
    ("jaipur", "Jaipur", "Rajasthan", 26.9124, 75.7873, []),
    ("delhi", "Delhi", "Delhi", 28.6139, 77.2090, ["New Delhi", "NCT of Delhi"]),
    ("mumbai", "Mumbai", "Maharashtra", 19.0760, 72.8777, ["Bombay", "Greater Mumbai"]),
    ("bengaluru", "Bengaluru", "Karnataka", 12.9716, 77.5946, ["Bangalore", "Bengalooru"]),
    ("hyderabad", "Hyderabad", "Telangana", 17.3850, 78.4867, ["Greater Hyderabad"]),
    ("chennai", "Chennai", "Tamil Nadu", 13.0827, 80.2707, ["Madras", "Greater Chennai"]),
    ("pune", "Pune", "Maharashtra", 18.5204, 73.8567, ["Poona"]),
    ("ahmedabad", "Ahmedabad", "Gujarat", 23.0225, 72.5714, ["Ahmadabad", "Amdavad"]),
]

UNVERIFIED = "To be verified in Phase 3"

SOURCES = [
    dict(
        name="OpenAQ",
        base_url="https://api.openaq.org/v3",
        access_method=AccessMethod.API.value,
        licence="Varies by data provider (see OpenAQ licences)",
        rate_limit_notes="Free tier: 60 requests/minute, 2,000/hour (docs.openaq.org, checked 2026-11-15). "
                         "Call from the backend only.",
        api_key_env_var="OPENAQ_API_KEY",
        description="Aggregated air quality measurements from government and other monitoring networks.",
    ),
    dict(
        name="data.gov.in (OGD Platform India)",
        base_url="https://data.gov.in/",
        access_method=AccessMethod.API.value,
        licence="Government Open Data License - India (GODL); verify per dataset",
        terms_url="https://data.gov.in/government-open-data-license-india",
        api_key_env_var="DATA_GOV_IN_API_KEY",
        description="National open data catalogue. Each API needs a resource ID; not every dataset has an API.",
    ),
    dict(
        name="Smart Cities Open Data Portal",
        base_url="https://smartcities.data.gov.in/",
        access_method=AccessMethod.CSV.value,
        licence=UNVERIFIED,
        description="City-published datasets from the Smart Cities Mission. Coverage varies by city.",
    ),
    dict(
        name="CPCB",
        base_url="https://cpcb.gov.in/",
        access_method=AccessMethod.CSV.value,
        licence=UNVERIFIED,
        description="Central Pollution Control Board air quality data, imported from downloaded files.",
    ),
    dict(
        name="Census of India",
        base_url="https://censusindia.gov.in/census.website/en/data",
        access_method=AccessMethod.CSV.value,
        licence=UNVERIFIED,
        description="Population and household statistics.",
    ),
    dict(
        name="OpenCity - Road Accidents in India 2024 (MoRTH)",
        base_url="https://data.opencity.in/dataset/road-accidents-in-india-2024",
        access_method=AccessMethod.CSV.value,
        licence="Other (Public Domain), as listed on the dataset page",
        description="MoRTH Transport Research Wing report data republished as CSV by OpenCity.",
    ),
    dict(
        name="OpenStreetMap",
        base_url="https://www.openstreetmap.in/",
        access_method=AccessMethod.API.value,
        licence="Open Database Licence (ODbL); attribution required, confirm in Phase 3",
        description="Geographic infrastructure and facility locations.",
    ),
    dict(
        name="SmartCity IQ manual and sample data",
        base_url=None,
        access_method=AccessMethod.MANUAL.value,
        licence="Not applicable",
        description="Hand-entered or illustrative rows. Always labelled manual_import or sample.",
    ),
]


def seed_reference(session) -> dict:
    created = {"cities": 0, "aliases": 0, "sources": 0}

    for slug, name, state, lat, lon, aliases in CITIES:
        city = session.scalar(select(City).where(City.slug == slug))
        if city is None:
            city = City(slug=slug, name=name, state=state, latitude=lat, longitude=lon)
            session.add(city)
            session.flush()
            created["cities"] += 1
        for alias in [name, *aliases]:
            key = normalize_name(alias)
            exists = session.scalar(select(CityAlias.id).where(CityAlias.alias_normalized == key))
            if exists is None:
                session.add(CityAlias(city_id=city.id, alias=alias, alias_normalized=key))
                created["aliases"] += 1

    for spec in SOURCES:
        if session.scalar(select(DataSource.id).where(DataSource.name == spec["name"])) is None:
            session.add(DataSource(**spec))
            created["sources"] += 1

    session.flush()
    return created


def main() -> None:
    from dotenv import load_dotenv

    from app import db
    from app.config import load_config

    load_dotenv()
    db.init_db(load_config()["DATABASE_URL"])
    with db.Session() as session:
        result = seed_reference(session)
        session.commit()
    print("Seeded:", result)


if __name__ == "__main__":
    main()
