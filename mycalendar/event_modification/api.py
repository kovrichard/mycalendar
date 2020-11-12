from datetime import datetime, timedelta

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_user import current_user, login_required

from mycalendar.db_models import db
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

    return __render_view(
        decoded_token["user_id"], True, user_name, token=token
    )


def __render_view(
    user_id, shared_calendar=False, shared_user_name="", token=""
):
    year = int(request.form["year"])
    week = int(request.form["week"])
    day = int(request.form["day"])
    hour = int(request.form["hour"])

    start_date = datetime.fromisocalendar(year, week, int(day) + 1).strftime(
        "%Y-%m-%d"
    )
    end_date = datetime.fromisocalendar(year, week, day + 1)
    start_time = hour_number_to_24_hours_format(str(hour))
    end_time = hour_number_to_24_hours_format(str(hour + 1))

    if hour == 23:
        end_date += timedelta(days=1)
    end_date = end_date.strftime("%Y-%m-%d")

    event = Event.query.filter(
        Event.start <= f"{start_date} {start_time}",
        Event.end >= f"{end_date} {end_time}",
        Event.user_id == user_id,
    ).first()

    return render_template(
        "event-modification.html",
        year_number=year,
        week_number=week,
        event=event,
        start_date=event.start.date() if event else start_date,
        start_time=event.start.time() if event else start_time,
        end_date=event.end.date() if event else end_date,
        end_time=event.end.time() if event else end_time,
        shared_calendar=shared_calendar,
        shared_user_name=shared_user_name,
        token=token,
    )


@event_mod_bp.route(
    "/register-guest/<string:token>", strict_slashes=False, methods=["POST"]
)
def register_guest(token):
    decoded_token = UserAccess(
        current_app.config["SHARING_TOKEN_SECRET"]
    ).decode(token)

    if not decoded_token:
        abort(401)

    event_id = request.form["event-id"]
    guest_name = request.form["guest-name"]

    if event := Event.query.filter_by(id=event_id).first():
        event.guest_name = guest_name
        db.session.add(event)
        db.session.commit()

    now = datetime.now().isocalendar()
    return redirect(
        url_for("week.shared_calendar", year=now[0], week=now[1], token=token),
        302,
    )
