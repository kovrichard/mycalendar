from datetime import datetime, timedelta

from flask import Blueprint, current_app, render_template, request
from flask.views import MethodView
from flask_user import current_user, login_required

from mycalendar.lib.user_access import UserAccess

share_bp = Blueprint("share", __name__, template_folder="templates")


class ShareAPI(MethodView):
    @login_required
    def get(self):
        return render_template(
            "share.html", expiration=datetime.now().date() + timedelta(days=7)
        )


@share_bp.route("/get-link", strict_slashes=False, methods=["GET"])
@login_required
def get_share_link():
    user_id = current_user.id
    expiration = datetime.strptime(request.args.get("expiration"), "%Y-%m-%d")
    share_content = (
        True if request.args.get("share-content") == "true" else False
    )
    now = datetime.now().isocalendar()

    return {
        "token": f"{current_app.config['CALENDAR_URL']}/{now[0]}/{now[1]}/shared-calendar/{UserAccess(current_app.config['SHARING_TOKEN_SECRET']).generate(user_id, expiration - datetime.now(), share_content)}"
    }


share_bp.add_url_rule(
    "/", strict_slashes=False, view_func=ShareAPI.as_view("share")
)
