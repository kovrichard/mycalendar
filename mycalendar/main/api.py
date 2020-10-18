from flask import Blueprint, render_template, current_app, request, redirect, url_for
from flask.views import MethodView
from flask_user import login_required
from datetime import datetime, date

main_bp = Blueprint("main", __name__, template_folder="templates")

@main_bp.route("/", methods=["GET"])
@login_required
def get_main():
    return redirect(url_for("week.get_week", week_num=datetime.now().isocalendar()[1]), 302)
