from datetime import datetime, timedelta

from flask import Blueprint, current_app, render_template, request
from flask_user import current_user, login_required

from mycalendar.db_models.event import Event
from mycalendar.db_models.user import User
from mycalendar.lib.datetime_calculator import hour_number_to_24_hours_format
from mycalendar.lib.user_access import UserAccess

event_mod_bp = Blueprint(
    "event_modification", __name__, template_folder="templates"
)


@event_mod_bp.route("/", strict_slashes=False, methods=["POST"])
@login_required
def event_mod():
    return __render_view(current_user.id)


@event_mod_bp.route("/<string:token>", strict_slashes=False, methods=["POST"])
def shared_event_view(token):
    decoded_token = UserAccess(
        current_app.config["SHARING_TOKEN_SECRET"]
    ).decode(token)

    if not decoded_token:
        abort(401)

    user_name = (
        User.query.filter_by(id=decoded_token["user_id"]).first().username
    )

    return __render_view(decoded_token["user_id"], True, user_name, token=token)


def __render_view(user_id, shared_calendar=False, shared_user_name="", token=""):
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

    event = Event.query.filter_by(
        start=f"{start_date} {start_time}",
        end=f"{end_date} {end_time}",
        user_id=user_id,
    ).first()

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
        event_type=event.event_type if event else "",
        shared_calendar=shared_calendar,
        shared_user_name=shared_user_name,
        token=token,
    )
