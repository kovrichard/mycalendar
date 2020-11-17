from datetime import datetime, timedelta

from flask import Blueprint, render_template, request
from flask_user import current_user, login_required

from mycalendar.db_models.db_event import Event
from mycalendar.lib.datetime_helper import DateTimeHelper

event_bp = Blueprint("event", __name__, template_folder="templates")
date_time_helper = DateTimeHelper()


@event_bp.route("/", strict_slashes=False, methods=["POST"])
@login_required
def event():
    year = int(request.form["year"])
    week = int(request.form["week"])
    day = int(request.form["day"])
    hour = int(request.form["hour"])

    start_date = datetime.fromisocalendar(year, week, int(day) + 1).strftime(
        "%Y-%m-%d"
    )
    end_date = datetime.fromisocalendar(year, week, day + 1)
    start_time = date_time_helper.hour_number_to_24_hours_format(str(hour))
    end_time = date_time_helper.hour_number_to_24_hours_format(str(hour + 1))

    if hour == 23:
        end_date += timedelta(days=1)
    end_date = end_date.strftime("%Y-%m-%d")

    event = Event.query.filter(
        Event.start <= f"{start_date} {start_time}",
        Event.end >= f"{end_date} {end_time}",
        Event.user_id == current_user.id,
    ).first()

    return render_template(
        "event.html",
        year_number=year,
        week_number=week,
        event=event,
        start_date=event.start.date() if event else start_date,
        start_time=event.start.time() if event else start_time,
        end_date=event.end.date() if event else end_date,
        end_time=event.end.time() if event else end_time,
    )
