from flask import Blueprint, render_template

week_bp = Blueprint("week", __name__, template_folder="templates")


@week_bp.route("/<int:week_num>", methods=["GET"])
def get_week(week_num):
    return render_template("week.html", week_number=week_num)
