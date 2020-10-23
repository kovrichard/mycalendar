from flask import Blueprint, render_template, request
from flask_user import login_required

from mycalendar.db_models import db
from mycalendar.db_models.event import Event

week_bp = Blueprint("week", __name__, template_folder="templates")


@week_bp.route("/<int:week_num>", methods=["GET", "POST"])
@login_required
def get_week(week_num):
    if request.method == "GET":
        return render_template("week.html", week_number=week_num)
    else:
        event_type = 1 if "business_hour" in request.form else 0

        event = Event(
            title=request.form["title"],
            description=request.form["description"],
            location=request.form["location"],
            start=request.form["start_date"]
            + " "
            + request.form["start_time"],
            end=request.form["end_date"] + " " + request.form["end_time"],
            event_type=event_type,
        )
        db.session.add(event)
        db.session.commit()

        return render_template("week.html", week_number=week_num)
