from datetime import datetime

from flask import Flask

from mycalendar.db_models import init_db
from mycalendar.main.api import main_bp


def create_app():
    app = Flask(__name__, template_folder="base_templates")

    app.register_blueprint(main_bp, url_prefix="/")

    app.jinja_env.globals["current_year"] = datetime.today().year

    init_db(app)

    return app
