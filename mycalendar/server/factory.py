from datetime import datetime

from flask import Flask

from mycalendar.event_modification.api import event_mod_bp
from mycalendar.main.api import main_bp
from mycalendar.share.api import share_bp
from mycalendar.week.api import week_bp


def create_app(config=None):
    app = Flask(__name__, template_folder="base_templates")
    app.config.from_object("mycalendar.server.config")

    if config is not None:
        for key in config:
            app.config[key] = config[key]

    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(week_bp, url_prefix="/")
    app.register_blueprint(event_mod_bp, url_prefix="/add-event")
    app.register_blueprint(share_bp, url_prefix="/share")

    app.jinja_env.globals["current_year"] = datetime.today().year

    __init_db(app)
    __init_user_manager(app)

    return app


def __init_db(app):
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DB_URL"]

    from mycalendar.db_models import init_db

    init_db(app)


def __init_user_manager(app):
    from flask_sqlalchemy import SQLAlchemy
    from flask_user import UserManager

    from mycalendar.db_models.user import User

    user_manager = UserManager(app, SQLAlchemy(app), User)

    return user_manager
