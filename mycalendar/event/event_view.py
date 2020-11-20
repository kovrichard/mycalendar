from flask import Blueprint, render_template, request
from flask.views import MethodView
from flask_user import current_user, login_required

from .event_controller import EventController

event_bp = Blueprint("event", __name__, template_folder="templates")


class EventView(MethodView):
    def __init__(self):
        self.__event_controller = EventController()

    @login_required
    def post(self):
        self.__event_controller.set_request(request)
        self.__event_controller.set_user(current_user)

        event = self.__event_controller.get_event()
        start_date = self.__event_controller.get_start_date()
        start_time = self.__event_controller.get_start_time()
        end_date = self.__event_controller.get_end_date()
        end_time = self.__event_controller.get_end_time()

        return render_template(
            "event.html",
            year_number=self.__event_controller.get_year(),
            week_number=self.__event_controller.get_week(),
            event=event,
            start_date=event.start.date() if event else start_date,
            start_time=event.start.time() if event else start_time,
            end_date=event.end.date() if event else end_date,
            end_time=event.end.time() if event else end_time,
        )


event_bp.add_url_rule(
    "/",
    strict_slashes=False,
    view_func=EventView.as_view("event_view"),
    methods=["POST"],
)
