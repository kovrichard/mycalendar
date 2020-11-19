from datetime import datetime

from flask import Flask

from mycalendar.event.event_view import event_bp
from mycalendar.main.main_view import main_bp
from mycalendar.share.share_link_creator import share_link_bp
from mycalendar.share.share_view import share_bp
from mycalendar.shared_view.shared_view import shared_view_bp
from mycalendar.week.week_view import week_bp


def create_app(config=None):
    app = Flask(__name__, template_folder="base_templates")
    app.config.from_object("mycalendar.server.config")

    if config is not None:
        for key in config:
            app.config[key] = config[key]

    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(week_bp, url_prefix="/")
    app.register_blueprint(event_bp, url_prefix="/event")
    app.register_blueprint(share_bp, url_prefix="/share")
    app.register_blueprint(share_link_bp, url_prefix="/get-share-link")
    app.register_blueprint(shared_view_bp, url_prefix="")

    app.jinja_env.globals["current_year"] = datetime.now().isocalendar()[0]
    app.jinja_env.globals["current_week"] = datetime.now().isocalendar()[1]

    __init_db(app)
    __init_user_manager(app)

    return app


def __init_db(app):
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DATABASE_URL"]

    from mycalendar.db_models import init_db

    init_db(app)


def __init_user_manager(app):
    from flask_sqlalchemy import SQLAlchemy
    from flask_user import UserManager

    from mycalendar.db_models.db_user import User

    user_manager = UserManager(app, SQLAlchemy(app), User)

    return user_manager
