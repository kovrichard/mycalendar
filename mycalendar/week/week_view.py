from flask import Blueprint, flash, render_template, request
from flask.views import MethodView
from flask_user import current_user, login_required

from mycalendar.lib.datetime_helper import DateTimeHelper
from mycalendar.week.week_controller import WeekController

from .week_controller import (
    DifferentDayEndError,
    EndBeforeStartError,
    OverlappingEventError,
)

week_bp = Blueprint("week", __name__, template_folder="templates")

date_time_helper = DateTimeHelper()


class WeekView(MethodView):
    def __init__(self):
        self.__week_controller = WeekController()

    @login_required
    def get(self, year, week):
        self.__week_controller.set_current_user(current_user)
        self.__week_controller.set_year(year)
        self.__week_controller.set_week(week)

        current_week = self.__week_controller.get_current_week()
        days_of_week = self.__week_controller.get_days_of_week()
        events = self.__week_controller.get_formatted_events()

        return render_template(
            "week.html",
            year_number=year,
            week_number=week,
            days_of_week=days_of_week,
            events=events,
        )

    @login_required
    def post(self, year, week):
        self.__week_controller.set_current_user(current_user)
        self.__week_controller.set_year(year)
        self.__week_controller.set_week(week)
        self.__week_controller.set_request(request)

        try:
            self.__week_controller.handle_post_request()
            days_of_week = self.__week_controller.get_days_of_week()
            events = self.__week_controller.get_formatted_events()
            return render_template(
                "week.html",
                year_number=year,
                week_number=week,
                days_of_week=days_of_week,
                events=events,
            )
        except OverlappingEventError:
            flash("Overlapping event!", "danger")
        except EndBeforeStartError:
            flash(
                "End of event cannot be earlier than (or equal to) its start!",
                "danger",
            )
        except DifferentDayEndError:
            flash("Event ends on a different day!", "danger")

        return render_template(
            "event.html",
            year_number=year,
            week_number=week,
            event=self.__week_controller.get_new_event(),
            start_date=request.form["start_date"],
            start_time=request.form["start_time"],
            end_date=request.form["end_date"],
            end_time=request.form["end_time"],
        )


week_bp.add_url_rule(
    "/<int:year>/<int:week>",
    view_func=WeekView.as_view("week"),
    methods=["GET", "POST"],
)
