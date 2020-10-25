from datetime import datetime

from flask import Blueprint, redirect, url_for
from mycalendar.lib.calculate_week import calculate_days_of_week

main_bp = Blueprint("main", __name__, template_folder="templates")


@main_bp.route("/", methods=["GET"])
def get_main():
    now = datetime.now().isocalendar()

    days_of_week = calculate_days_of_week(now[0], now[1])

    return redirect(url_for("week.get_week", year=now[0], week=now[1], days_of_week=days_of_week), 302)
