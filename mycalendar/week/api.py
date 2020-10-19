from datetime import datetime

from flask import Blueprint, render_template
from flask_user import login_required

week_bp = Blueprint("week", __name__, template_folder="templates")


@week_bp.route("/<int:week_num>", methods=["GET"])
@login_required
# @roles_required(["user", "admin"])
def get_week(week_num):
    return render_template(
        "week.html",
        week_number=week_num,
        current_week=datetime.now().isocalendar()[1],
    )
