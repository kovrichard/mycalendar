from datetime import datetime, timedelta

from flask import Blueprint, current_app, render_template, request
from flask_user import current_user, login_required

from mycalendar.lib.user_access import UserAccess

share_bp = Blueprint("share", __name__, template_folder="templates")


@share_bp.route("/", strict_slashes=False, methods=["GET"])
@login_required
def share():
    return render_template(
        "share.html", expiration=datetime.now().date() + timedelta(days=7)
    )


@share_bp.route("/get-link", strict_slashes=False, methods=["GET"])
@login_required
def get_share_link():
    user_id = current_user.id
    expiration = datetime.strptime(request.args.get("expiration"), "%Y-%m-%d")
    share_all = request.args.get("share-content")
    now = datetime.now().isocalendar()

    return {
        "token": f"{current_app.config['CALENDAR_URL']}/{now[0]}/{now[1]}/shared-calendar/{UserAccess(current_app.config['SHARING_TOKEN_SECRET']).generate(user_id, expiration - datetime.now(), share_all)}"
    }
