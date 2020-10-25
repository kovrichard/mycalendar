from datetime import datetime

from flask import Blueprint, render_template, request
from flask_user import current_user, login_required

from mycalendar.db_models.event import Event

event_mod_bp = Blueprint(
    "event_modification", __name__, template_folder="templates"
)


@event_mod_bp.route("/", strict_slashes=False, methods=["POST"])
@login_required
def event_mod():
    year = request.form["year"]
    week = request.form["week"]
    hour = request.form["hour"]
    day = request.form["day"]

    start_date = isocalendar_to_normal_date(year, week, day)
    start_time, end_time = hour_number_to_24_hours_format(hour)

    event = Event.query.filter_by(
        start=f"{start_date} {start_time}",
        end=f"{start_date} {end_time}",
        user_id=current_user.id,
    ).first()

    if event and event.event_type == 1:
        event_type = "checked"
    else:
        event_type = ""

    return render_template(
        "event-modification.html",
        year_number=year,
        week_num=week,
        title=event.title if event else "",
        description=event.description if event else "",
        location=event.location if event else "",
        start_date=event.start.date() if event else start_date,
        start_time=event.start.time() if event else start_time,
        end_date=event.end.date() if event else start_date,
        end_time=event.end.time() if event else end_time,
        event_type=event_type,
    )


def isocalendar_to_normal_date(year, week, day):
    return datetime.fromisocalendar(
        int(year), int(week), int(day) + 1
    ).strftime("%Y-%m-%d")


def hour_number_to_24_hours_format(hour):
    start = ("0" + hour if len(hour) < 2 else hour) + ":00"
    tmp = str(int(hour) + 1)
    end = ("0" + tmp if len(tmp) < 2 else tmp) + ":00"
    return start, end
