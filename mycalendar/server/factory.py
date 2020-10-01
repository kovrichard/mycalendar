from datetime import datetime

from flask import Flask

from mycalendar.main.api import main_bp


def create_app(config=None):
    app = Flask(__name__, template_folder="base_templates")
    app.config.from_object("mycalendar.server.config")

    if config is not None:
        for key in config:
            app.config[key] = config[key]

    app.register_blueprint(main_bp, url_prefix="/")

    app.jinja_env.globals["current_year"] = datetime.today().year

    __init_db(app)

    return app


def __init_db(app):
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DB_URL"]

    from mycalendar.db_models import init_db

    init_db(app)
