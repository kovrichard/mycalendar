from flask import Flask

from mycalendar.main.api import main_bp


def create_app():
    app = Flask(__name__, template_folder="base_templates")

    app.register_blueprint(main_bp, url_prefix="/")

    return app
