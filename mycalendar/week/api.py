from flask import Blueprint, abort, current_app, render_template, request
from flask_user import current_user, login_required

from mycalendar.db_models import db
from mycalendar.db_models.event import Event
from mycalendar.db_models.user import User
from mycalendar.db_models.week import Week
from mycalendar.lib.datetime_calculator import (
    calculate_days_of_week,
    calculate_different_year,
)
from mycalendar.lib.user_access import UserAccess

week_bp = Blueprint("week", __name__, template_folder="templates")


@week_bp.route("/<int:year>/<int:week>", methods=["GET", "POST"])
@login_required
def get_week(year, week):
    year, week = calculate_different_year(year, week)

    if request.method == "GET":
        return handle_get(year, week)
    else:
        return handle_post(year, week)


def handle_get(year, week):
    current_week = __persist_week_to_db(year, week)
    days_of_week = calculate_days_of_week(year, week)

    events = Event.query.filter_by(
        week_id=current_week.id, user_id=current_user.id
    ).all()

    return render_template(
        "week.html",
        year_number=year,
        week_number=week,
        days_of_week=days_of_week,
        events=__refactor(events),
    )


def handle_post(year, week):
    event_type = 1 if "business_hour" in request.form else 0

    if current_week := Week.query.filter_by(year=year, week_num=week).first():
        event = Event.query.filter_by(
            start=f"{request.form['start_date']} {request.form['start_time']}",
            end=f"{request.form['end_date']} {request.form['end_time']}",
            user_id=current_user.id,
        ).first()

        if request.form["action"] == "Save":
            if event:
                __modify_event(event, event_type)
            else:
                __insert_new_event(current_week, event_type)
        elif event:
            Event.query.filter_by(
                start=event.start, end=event.end, user_id=event.user_id
            ).delete()

        db.session.commit()

    days_of_week = calculate_days_of_week(year, week)

    events = Event.query.filter_by(
        week_id=current_week.id, user_id=current_user.id
    ).all()

    return render_template(
        "week.html",
        year_number=year,
        week_number=week,
        days_of_week=days_of_week,
        events=__refactor(events),
    )


def __persist_week_to_db(year, week):
    tmp = Week.query.filter_by(year=year, week_num=week).first()

    if tmp is None:
        tmp = Week(year=year, week_num=week)
        db.session.add(tmp)
        db.session.commit()

    return tmp


def __modify_event(event, event_type):
    event.title = request.form["title"]
    event.description = request.form["description"]
    event.location = request.form["location"]
    event.event_type = event_type
    event.guest_name = request.form["guest-name"] if event_type == 1 else ""


def __insert_new_event(current_week, event_type):
    event = Event(
        title=request.form["title"],
        description=request.form["description"],
        location=request.form["location"],
        start=f"{request.form['start_date']} {request.form['start_time']}",
        end=f"{request.form['end_date']} {request.form['end_time']}",
        event_type=event_type,
        guest_name=request.form["guest-name"] if event_type == 1 else "",
    )
    db.session.add(event)

    current_week.events.append(event)
    current_user.events.append(event)


def __refactor(events):
    tmp = []

    for e in events:
        item = {}
        item["title"] = e.title
        item["location"] = e.location
        item["day"] = e.start.date().isocalendar()[2] - 1
        item["hour"] = [
            h for h in range(e.start.time().hour, e.end.time().hour)
        ]
        item["type"] = "active-event"

        tmp.append(item)

    return tmp


@week_bp.route(
    "/<int:year>/<int:week>/shared-calendar/<string:token>",
    methods=["GET", "POST"],
)
def shared_calendar(year, week, token):
    decoded_token = UserAccess(
        current_app.config["SHARING_TOKEN_SECRET"]
    ).decode(token)

    if not decoded_token:
        abort(401)

    year, week = calculate_different_year(year, week)

    if request.method == "GET":
        return __handle_shared_get(year, week, decoded_token, token)
    else:
        return __handle_shared_post(year, week)


def __handle_shared_get(year, week, decoded_token, token):
    current_week = __persist_week_to_db(year, week)
    days_of_week = calculate_days_of_week(year, week)

    events = Event.query.filter_by(
        week_id=current_week.id, user_id=decoded_token["user_id"]
    ).all()

    return render_template(
        "week.html",
        year_number=year,
        week_number=week,
        days_of_week=days_of_week,
        events=__refactor(events),
        shared_calendar=True,
        share_content=decoded_token["share_content"],
        shared_user=User.query.filter_by(id=decoded_token["user_id"]).first(),
        token=token,
    )


def __handle_shared_post(year, week):
    return "OK", 200
