from datetime import datetime

from flask import Blueprint, redirect, url_for
from flask_user import login_required

main_bp = Blueprint("main", __name__, template_folder="templates")


@main_bp.route("/", methods=["GET"])
@login_required
def get_main():
    return redirect(
        url_for("week.get_week", week_num=datetime.now().isocalendar()[1]), 302
    )
