# Architecture (approved in Phase 1)

```
Sources -> Connectors -> Raw landing -> Pandas pipeline -> PostgreSQL -> Flask API -> React app
```

- One connector class per provider, each implementing `fetch -> parse -> normalize -> validate -> load`.
- Adding a city means adding a `cities` row and aliases. No code changes.
- Every API response carries `meta`: source, dataset, data class, geographic level, period, last
  updated, record count and warnings. The UI renders unavailable-data and missing-data notices from it.
- Charts use Plotly only (Chart.js dropped). Maps use React-Leaflet.
- OpenAQ is called from the backend only (rate limits and CORS).

## Schema (13 tables)
cities, city_aliases, data_sources, datasets, stations, air_quality, traffic_statistics,
road_accidents, water_statistics, population_statistics, infrastructure, import_batches,
data_refresh_logs.

### Change from the Phase 1 proposal: `record_key`
Phase 1 proposed unique constraints on natural keys. Several keys contain nullable columns, and
PostgreSQL treats NULLs as distinct, so those constraints would not stop duplicates. Each fact row
instead carries a unique `record_key`, a SHA-256 of its natural key (`app/utils/keys.py`), and
imports upsert on it. Reference tables keep ordinary unique constraints.

### Database-level quality rules
- `data_class`, `geo_level`, pollutant and category values are restricted to fixed vocabularies.
- A row must either have a value or be explicitly marked `is_missing`.
- A value must have a unit. Original value and unit are kept next to the normalized ones.
- City-level and state-level rows must name their city or state.
- Counts are non-negative; periods cannot end before they start.
- City centroids must fall inside India's bounding box. Station and facility coordinates are kept raw
  with a `coords_valid` flag, so invalid ones are flagged rather than dropped.
