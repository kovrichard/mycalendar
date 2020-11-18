from datetime import datetime, timedelta

from flask import Blueprint, current_app, render_template, request
from flask.views import MethodView
from flask_user import current_user, login_required

from mycalendar.lib.user_access import UserAccess

share_bp = Blueprint("share", __name__, template_folder="templates")


class ShareView(MethodView):
    @login_required
    def get(self):
        return render_template(
            "share.html", expiration=datetime.now().date() + timedelta(days=7)
        )


class ShareLink(MethodView):
    @login_required
    def get(self):
        user_id = current_user.id
        expiration = datetime.strptime(
            request.args.get("expiration"), "%Y-%m-%d"
        )
        share_content = (
            True if request.args.get("share-content") == "true" else False
        )

        return self.__create_shareable_token(
            user_id, expiration, share_content
        )

    def __create_shareable_token(self, user_id, expiration, share_content):
        now = datetime.now().isocalendar()

        return {
            "token": f"{current_app.config['CALENDAR_URL']}/{now[0]}/{now[1]}/shared-calendar/{UserAccess(current_app.config['SHARING_TOKEN_SECRET']).generate(user_id, expiration - datetime.now(), share_content)}"
        }


share_bp.add_url_rule(
    "/",
    strict_slashes=False,
    view_func=ShareView.as_view("share"),
    methods=["GET"],
)

share_bp.add_url_rule(
    "/get-link",
    strict_slashes=False,
    view_func=ShareLink.as_view("sharelink"),
    methods=["GET"],
)
