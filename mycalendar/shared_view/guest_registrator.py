from datetime import datetime

from flask import Blueprint, abort, current_app, redirect, request, url_for

from mycalendar.db_models import db
from mycalendar.db_models.db_event import Event
from mycalendar.lib.user_access import UserAccess

register_guest_bp = Blueprint(
    "register_guest", __name__, template_folder="templates"
)


@register_guest_bp.route(
    "/<string:token>", strict_slashes=False, methods=["POST"]
)
def post(token):
    guest_registrator = GuestRegistrator(token, request)

    if not guest_registrator.get_decoded_token():
        abort(401)

    return redirect(
        url_for(
            "shared_view.week",
            year=guest_registrator.get_year(),
            week=guest_registrator.get_week(),
            token=token,
        ),
        302,
    )


class GuestRegistrator:
    def __init__(self, token, request):
        self.__token = token
        self.__request = request

        if self.get_decoded_token():
            self.__save_guest_name()

    def get_decoded_token(self):
        return UserAccess(current_app.config["SHARING_TOKEN_SECRET"]).decode(
            self.__token
        )

    def get_year(self):
        return datetime.now().isocalendar()[0]

    def get_week(self):
        return datetime.now().isocalendar()[1]

    def __save_guest_name(self):
        event_id = self.__request.form["event-id"]
        guest_name = self.__request.form["guest-name"]

        if event := Event.query.get(event_id):
            event.guest_name = guest_name
            db.session.add(event)
            db.session.commit()
