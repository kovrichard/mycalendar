from flask import Blueprint, flash, render_template, request
from flask.views import MethodView
from flask_user import current_user, login_required

from mycalendar.db_models import db
from mycalendar.db_models.db_event import Event
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

        event_type = self.__week_controller.get_event_type_from_request()

        current_week = self.__week_controller.get_current_week()
        event = Event.query.filter_by(id=request.form["event-id"]).first()

        if request.form["action"] == "Save":
            if event:
                new_event = self.__week_controller.modify_event(
                    event, event_type
                )
            else:
                new_event = self.__week_controller.insert_new_event(
                    current_week, event_type
                )

            try:
                self.__week_controller.check_event(new_event)
                db.session.commit()
            except OverlappingEventError as o:
                flash("Overlapping event!", "danger")
                db.session.rollback()
                return self.__return_to_modification(year, week, new_event)
            except EndBeforeStartError as e:
                flash(
                    "End of event cannot be earlier than (or equal to) its start!",
                    "danger",
                )
                db.session.rollback()
                return self.__return_to_modification(year, week, new_event)
            except DifferentDayEndError as d:
                flash("Event ends on a different day!", "danger")
                db.session.rollback()
                return self.__return_to_modification(year, week, new_event)
        else:
            self.__week_controller.delete_event(event)

        days_of_week = self.__week_controller.get_days_of_week()
        events = self.__week_controller.get_formatted_events()

        return render_template(
            "week.html",
            year_number=year,
            week_number=week,
            days_of_week=days_of_week,
            events=events,
        )

    def __return_to_modification(self, year, week, new_event):
        return render_template(
            "event.html",
            year_number=year,
            week_number=week,
            event=new_event,
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
