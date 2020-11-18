from datetime import datetime

from flask import Blueprint, current_app, request
from flask_user import current_user, login_required

from mycalendar.lib.user_access import UserAccess

share_link_bp = Blueprint("share_link", __name__, template_folder="templates")


@share_link_bp.route("/", strict_slashes=False, methods=["GET"])
@login_required
def get():
    share_link_creator = ShareLinkCreator(current_user.id, request)

    return share_link_creator.create_shareable_token()


class ShareLinkCreator:
    def __init__(self, user_id, _request):
        self.__user_id = user_id
        self.__request = _request

    def __get_expiration(self):
        return datetime.strptime(
            self.__request.args.get("expiration"), "%Y-%m-%d"
        )

    def __get_share_content(self):
        return (
            True
            if self.__request.args.get("share-content") == "true"
            else False
        )

    def create_shareable_token(self):
        now = datetime.now().isocalendar()

        jwt_token = UserAccess(
            current_app.config["SHARING_TOKEN_SECRET"]
        ).generate(
            self.__user_id,
            self.__get_expiration() - datetime.now(),
            self.__get_share_content(),
        )

        token = f"{current_app.config['CALENDAR_URL']}/{now[0]}/{now[1]}"
        token = f"{token}/shared-calendar/{jwt_token}"

        return {"token": token}
