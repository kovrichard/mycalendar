from datetime import datetime

from flask import Blueprint, redirect, url_for
from flask.views import MethodView

from mycalendar.lib.datetime_helper import DateTimeHelper

main_bp = Blueprint("main", __name__, template_folder="templates")

date_time_helper = DateTimeHelper()


class MainView(MethodView):
    def get(self):
        now = datetime.now().isocalendar()

        days_of_week = date_time_helper.calculate_days_of_week(now[0], now[1])

        return redirect(
            url_for(
                "week.week",
                year=now[0],
                week=now[1],
                days_of_week=days_of_week,
            ),
            302,
        )


main_bp.add_url_rule("/", view_func=MainView.as_view("main"), methods=["GET"])
