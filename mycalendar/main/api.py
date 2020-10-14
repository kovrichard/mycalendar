from flask import Blueprint, render_template
from flask.views import MethodView

main_bp = Blueprint("main", __name__, template_folder="templates")


class CalendarController(MethodView):
    def get(self):
        return render_template("welcome.html")

    def post(self):
        return render_template("welcome.html")


main_bp.add_url_rule("/", view_func=CalendarController.as_view("calendar"))
