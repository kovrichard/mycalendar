from datetime import datetime

from flask import Blueprint, redirect, url_for

main_bp = Blueprint("main", __name__, template_folder="templates")


@main_bp.route("/", methods=["GET"])
def get_main():
    return redirect(
        url_for("week.get_week", week=datetime.now().isocalendar()[1]), 302
    )
