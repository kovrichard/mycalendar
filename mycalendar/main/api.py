import random

from flask import Blueprint, current_app, render_template, request
from flask.views import MethodView

from mycalendar.db_models import db
from mycalendar.db_models.user import User

main_bp = Blueprint("main", __name__, template_folder="templates")


class CalendarController(MethodView):
    def get(self):
        db.session.add(
            User(username="mas" + str(random.randint(1, 100000)), password="pw")
        )
        db.session.commit()

        return render_template("welcome.html")

    def post(self):
        return render_template("welcome.html")


main_bp.add_url_rule("/", view_func=CalendarController.as_view("calendar"))
