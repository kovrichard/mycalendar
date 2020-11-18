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

from mycalendar.db_models import db
from mycalendar.db_models.db_event import Event
from mycalendar.db_models.db_user import User
from mycalendar.db_models.db_week import Week
from mycalendar.lib.datetime_helper import DateTimeHelper
from mycalendar.lib.user_access import UserAccess

shared_view_bp = Blueprint(
    "shared_view", __name__, template_folder="templates"
)
date_time_helper = DateTimeHelper()


@shared_view_bp.route(
    "/shared-event/<string:token>", strict_slashes=False, methods=["POST"]
)
def shared_event_view(token):
    decoded_token = UserAccess(
        current_app.config["SHARING_TOKEN_SECRET"]
    ).decode(token)

    if not decoded_token:
        abort(401)

    user_name = (
        User.query.filter_by(id=decoded_token["user_id"]).first().username
    )

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
        Event.user_id == decoded_token["user_id"],
    ).first()

    return render_template(
        "shared-event.html",
        year_number=year,
        week_number=week,
        event=event,
        start_date=event.start.date() if event else start_date,
        start_time=event.start.time() if event else start_time,
        end_date=event.end.date() if event else end_date,
        end_time=event.end.time() if event else end_time,
        shared_user_name=user_name,
        token=token,
    )


@shared_view_bp.route(
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
        url_for(
            "shared_view.shared_calendar",
            year=now[0],
            week=now[1],
            token=token,
        ),
        302,
    )


@shared_view_bp.route(
    "/<int:year>/<int:week>/shared-calendar/<string:token>",
    methods=["GET"],
)
def shared_calendar(year, week, token):
    decoded_token = UserAccess(
        current_app.config["SHARING_TOKEN_SECRET"]
    ).decode(token)

    if not decoded_token:
        abort(401)

    year, week = date_time_helper.calculate_different_year(year, week)

    return __handle_shared_get(year, week, decoded_token, token)


def __handle_shared_get(year, week, decoded_token, token):
    current_week = __persist_week_to_db(year, week)
    days_of_week = date_time_helper.calculate_days_of_week(year, week)

    events = Event.query.filter_by(
        week_id=current_week.id, user_id=decoded_token["user_id"]
    ).all()

    return render_template(
        "shared-week.html",
        year_number=year,
        week_number=week,
        days_of_week=days_of_week,
        events=__format_for_render(events),
        shared_calendar=True,
        share_content=decoded_token["share_content"],
        shared_user_name=User.query.filter_by(id=decoded_token["user_id"])
        .first()
        .username,
        token=token,
    )


def __persist_week_to_db(year, week):
    tmp = Week.query.filter_by(year=year, week_num=week).first()

    if tmp is None:
        tmp = Week(year=year, week_num=week)
        db.session.add(tmp)
        db.session.commit()

    return tmp


def __format_for_render(events):
    tmp = []

    for e in events:
        item = {}
        item["title"] = e.title
        item["location"] = e.location
        item["day"] = e.start.date().isocalendar()[2] - 1
        item["hour"] = [
            h
            for h in range(
                e.start.time().hour,
                24 if e.end.time().hour == 0 else e.end.time().hour,
            )
        ]
        item["type"] = "active-event"

        tmp.append(item)

    return tmp
