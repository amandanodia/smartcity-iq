"""Deterministic record keys used to avoid duplicates on repeated imports.

Unique constraints over nullable natural-key columns do not de-duplicate in
PostgreSQL (NULLs are distinct), so every fact row carries a ``record_key``:
a SHA-256 digest of its natural key. Callers pass the table name first.
"""
import hashlib
from datetime import date, datetime, timezone

_SEP = "\x1f"
_NULL = "\x00"


def _normalise(part) -> str:
    if part is None:
        return _NULL
    if isinstance(part, float) and part != part:  # NaN is treated as missing
        return _NULL
    if isinstance(part, datetime):
        if part.tzinfo is None:
            raise ValueError("Naive datetime in record key; normalise to a timezone first.")
        return part.astimezone(timezone.utc).isoformat()
    if isinstance(part, date):
        return part.isoformat()
    if isinstance(part, bool):
        return "true" if part else "false"
    return str(part).strip().casefold()


def make_record_key(*parts) -> str:
    joined = _SEP.join(_normalise(p) for p in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
