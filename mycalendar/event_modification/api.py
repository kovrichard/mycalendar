from datetime import datetime

from flask import Blueprint, render_template, request
from flask_user import login_required

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

    return render_template(
        "event-modification.html",
        week_num=request.form["week_num"],
        start_date=start_date,
        start_time=start_time,
        end_time=end_time,
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
