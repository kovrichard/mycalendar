from datetime import datetime, timedelta

from flask import Blueprint, abort, current_app, render_template, request
from flask.views import MethodView

from mycalendar.db_models.db_event import Event
from mycalendar.db_models.db_user import User
from mycalendar.lib.datetime_helper import DateTimeHelper
from mycalendar.lib.user_access import UserAccess
from mycalendar.shared_view.shared_week_controller import SharedWeekController

shared_view_bp = Blueprint(
    "shared_view", __name__, template_folder="templates"
)
date_time_helper = DateTimeHelper()


class SharedEventView(MethodView):
    def post(self, token):
        decoded_token = UserAccess(
            current_app.config["SHARING_TOKEN_SECRET"]
        ).decode(token)

        if not decoded_token:
            abort(401)

        user_name = User.query.get(decoded_token["user_id"]).username

        year = int(request.form["year"])
        week = int(request.form["week"])
        day = int(request.form["day"])
        hour = int(request.form["hour"])

        start_date = datetime.fromisocalendar(
            year, week, int(day) + 1
        ).strftime("%Y-%m-%d")
        end_date = datetime.fromisocalendar(year, week, day + 1)
        start_time = date_time_helper.hour_number_to_24_hours_format(str(hour))
        end_time = date_time_helper.hour_number_to_24_hours_format(
            str(hour + 1)
        )

        if hour == 23:
            end_date += timedelta(days=1)
        end_date = end_date.strftime("%Y-%m-%d")

        event = Event.query.filter(
            Event.start <= f"{start_date} {start_time}",
            Event.end >= f"{end_date} {end_time}",
            Event.user_id == decoded_token["user_id"],
        ).first()

        return render_template(
            "shared-event.html",
            year_number=year,
            week_number=week,
            event=event,
            start_date=event.start.date() if event else start_date,
            start_time=event.start.time() if event else start_time,
            end_date=event.end.date() if event else end_date,
            end_time=event.end.time() if event else end_time,
            shared_user_name=user_name,
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
