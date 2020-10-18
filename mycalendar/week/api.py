from flask import Blueprint, render_template, current_app, request, redirect, url_for
import requests
from flask.views import MethodView
from flask_user import login_required
from datetime import datetime, date

week_bp = Blueprint("week", __name__, template_folder="templates")

@week_bp.route("/<int:week_num>", methods=["GET"])
def get_week(week_num):
    return render_template("week.html", week_number=week_num)
