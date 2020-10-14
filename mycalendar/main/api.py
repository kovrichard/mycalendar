import random

from flask import Blueprint, render_template
from flask.views import MethodView

from mycalendar.db_models import session
from mycalendar.db_models.user import User

main_bp = Blueprint("main", __name__, template_folder="templates")


class CalendarController(MethodView):
    def get(self):
        user = User(username="mas" + str(random.randint(1, 100000)), password="pw")
        session.add(user)
        session.commit()

        return render_template("welcome.html")

    def post(self):
        return render_template("welcome.html")


main_bp.add_url_rule("/", view_func=CalendarController.as_view("calendar"))
