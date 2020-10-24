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
    week_num = request.form["week_num"]
    n = request.form["n"]
    m = request.form["m"]

    start_date = refact(week_num, m)
    start_time, end_time = refact2(n)

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
        year_number=2020,
        week_num=request.form["week_num"],
        title=event.title if event else "",
        description=event.description if event else "",
        location=event.location if event else "",
        start_date=event.start.date() if event else start_date,
        start_time=event.start.time() if event else start_time,
        end_date=event.end.date() if event else start_date,
        end_time=event.end.time() if event else end_time,
        event_type=event_type,
    )


def refact(week_num, m):
    return datetime.fromisocalendar(2020, int(week_num), int(m) + 1).strftime(
        "%Y-%m-%d"
    )


def refact2(n):
    start = "0" + n + ":00" if len(n) < 2 else n + ":00"
    tmp = str(int(n) + 1)
    end = "0" + tmp + ":00" if len(tmp) < 2 else tmp + ":00"
    return start, end
