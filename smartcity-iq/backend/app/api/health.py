from flask import Blueprint, jsonify
from sqlalchemy import text

from app import db

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    try:
        db.Session.execute(text("SELECT 1"))
        ok = True
    except Exception:
        db.Session.rollback()
        ok = False
    body = {"status": "ok" if ok else "degraded", "database": "up" if ok else "down"}
    return jsonify(body), (200 if ok else 503)
