from datetime import datetime, timedelta

from flask import Blueprint, current_app, render_template, request
from flask_user import current_user, login_required

from mycalendar.db_models.event import Event
from mycalendar.lib.datetime_calculator import hour_number_to_24_hours_format

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

    start_date = datetime.fromisocalendar(
        int(year), int(week), int(day) + 1
    ).strftime("%Y-%m-%d")
    end_date = datetime.fromisocalendar(int(year), int(week), int(day) + 1)
    start_time = hour_number_to_24_hours_format(hour)
    end_time = hour_number_to_24_hours_format(str(int(hour) + 1))

    if int(hour) == 23:
        end_date += timedelta(days=1)
    end_date = end_date.strftime("%Y-%m-%d")

    current_app.logger.info(end_date)

    event = Event.query.filter_by(
        start=f"{start_date} {start_time}",
        end=f"{end_date} {end_time}",
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
        end_date=event.end.date() if event else end_date,
        end_time=event.end.time() if event else end_time,
        event_type=event_type,
    )
