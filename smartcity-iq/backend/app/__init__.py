from flask import Flask


def create_app(overrides: dict | None = None) -> Flask:
    # Imported here so config/utils stay importable without a database driver.
    from app import db
    from app.api.health import bp as health_bp
    from app.config import load_config

    flask_app = Flask(__name__)
    flask_app.config.update(load_config())
    if overrides:
        flask_app.config.update(overrides)

    db.init_db(flask_app.config["DATABASE_URL"])
    flask_app.register_blueprint(health_bp, url_prefix="/api")

    @flask_app.teardown_appcontext
    def _remove_session(_exc=None):
        db.Session.remove()

    return flask_app
