from flask import Blueprint, abort, render_template, request
from flask.views import MethodView

from mycalendar.lib.datetime_helper import DateTimeHelper
from mycalendar.shared_view.shared_event_controller import (
    SharedEventController,
)
from mycalendar.shared_view.shared_week_controller import SharedWeekController

shared_view_bp = Blueprint(
    "shared_view", __name__, template_folder="templates"
)
date_time_helper = DateTimeHelper()


class SharedEventView(MethodView):
    def __init__(self):
        self.__shared_event_controller = SharedEventController()

    def post(self, token):
        self.__shared_event_controller.set_token(token)
        self.__shared_event_controller.set_request(request)

        if not self.__shared_event_controller.get_decoded_token():
            abort(401)

        start_date = self.__shared_event_controller.get_start_date()
        start_time = self.__shared_event_controller.get_start_time()
        end_date = self.__shared_event_controller.get_end_date()
        end_time = self.__shared_event_controller.get_end_time()
        event = self.__shared_event_controller.get_event()

        return render_template(
            "shared-event.html",
            year_number=self.__shared_event_controller.get_year(),
            week_number=self.__shared_event_controller.get_week(),
            event=event,
            start_date=event.start.date() if event else start_date,
            start_time=event.start.time() if event else start_time,
            end_date=event.end.date() if event else end_date,
            end_time=event.end.time() if event else end_time,
            shared_user_name=self.__shared_event_controller.get_shared_user_name(),
            token=token,
        )


class SharedWeekView(MethodView):
    def __init__(self):
        self.__shared_week_controller = SharedWeekController()

    def get(self, year, week, token):
        self.__shared_week_controller.set_year_and_week(year, week)
        self.__shared_week_controller.set_token(token)

        if not self.__shared_week_controller.get_decoded_token():
            abort(401)

        days_of_week = self.__shared_week_controller.get_days_of_week()
        events = self.__shared_week_controller.get_formatted_events()

        return render_template(
            "shared-week.html",
            year_number=self.__shared_week_controller.get_year(),
            week_number=self.__shared_week_controller.get_week(),
            days_of_week=days_of_week,
            events=events,
            shared_calendar=True,
            share_content=self.__shared_week_controller.get_share_content(),
            shared_user_name=self.__shared_week_controller.get_shared_user_name(),
            token=token,
        )


shared_view_bp.add_url_rule(
    "/shared-event/<string:token>",
    strict_slashes=False,
    view_func=SharedEventView.as_view("event"),
    methods=["POST"],
)

shared_view_bp.add_url_rule(
    "/<int:year>/<int:week>/shared-calendar/<string:token>",
    view_func=SharedWeekView.as_view("week"),
    methods=["GET"],
)
