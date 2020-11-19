import datetime

from flask import Blueprint, flash, render_template, request
from flask.views import MethodView
from flask_user import current_user, login_required

from mycalendar.db_models import db
from mycalendar.db_models.db_event import Event
from mycalendar.db_models.db_week import Week
from mycalendar.lib.datetime_helper import DateTimeHelper
from mycalendar.week.week_controller import WeekController

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

        if current_week := Week.query.filter_by(
            year=year, week_num=week
        ).first():
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
                    self.__check_event(new_event)
                    db.session.commit()
                except OverlappingEventError as o:
                    db.session.rollback()
                    return self.__return_to_modification(year, week, new_event)
                except EndBeforeStartError as e:
                    db.session.rollback()
                    return self.__return_to_modification(year, week, new_event)
                except DifferentDayEndError as d:
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

    def __modify_event(self, event, event_type):
        start_time = self.__format_time(request.form["start_time"])
        end_time = self.__format_time(request.form["end_time"])

        event.title = request.form["title"]
        event.description = request.form["description"]
        event.location = request.form["location"]
        event.start = f"{request.form['start_date']} {start_time}"
        event.end = f"{request.form['end_date']} {end_time}"
        event.event_type = event_type
        event.guest_name = (
            request.form["guest-name"] if event_type == 1 else ""
        )

        return event

    def __insert_new_event(self, current_week, event_type):
        start_time = self.__format_time(request.form["start_time"])
        end_time = self.__format_time(request.form["end_time"])

        event = Event(
            title=request.form["title"],
            description=request.form["description"],
            location=request.form["location"],
            start=f"{request.form['start_date']} {start_time}",
            end=f"{request.form['end_date']} {end_time}",
            event_type=event_type,
            guest_name=request.form["guest-name"] if event_type == 1 else "",
        )
        db.session.add(event)

        current_week.events.append(event)
        current_user.events.append(event)

        return event

    def __format_time(self, time_string):
        try:
            datetime.datetime.strptime(time_string, "%H:%M:%S")
            return time_string
        except ValueError:
            return f"{time_string}:00"

    def __format_for_render(self, events):
        tmp = []

        for e in events:
            item = {}
            item["title"] = e.title
            item["location"] = e.location
            item["day"] = e.start.date().isocalendar()[2] - 1
            item["hour"] = [
                h
                for h in range(
                    e.start.time().hour,
                    24 if e.end.time().hour == 0 else e.end.time().hour,
                )
            ]
            item["type"] = "active-event"

            tmp.append(item)

        return tmp

    def __check_event(self, new_event):
        self.__overlapping_event(new_event)
        self.__event_end_is_earlier_than_start(new_event)
        self.__event_ends_on_different_day(new_event)

    def __overlapping_event(self, new_event):
        wrong_events = Event.query.filter(
            (Event.id != new_event.id)
            & (
                (
                    (new_event.start <= Event.start)
                    & (Event.start < new_event.end)
                )
                | (
                    (new_event.start < Event.end)
                    & (Event.end <= new_event.end)
                )
            )
        ).all()

        if len(wrong_events) > 0:
            flash("Overlapping event!", "danger")
            raise OverlappingEventError

    def __event_end_is_earlier_than_start(self, new_event):
        if new_event.end <= new_event.start:
            flash(
                "End of event cannot be earlier than (or equal to) its start!",
                "danger",
            )
            raise EndBeforeStartError

    def __event_ends_on_different_day(self, new_event):
        start = datetime.datetime.strptime(
            new_event.start, "%Y-%m-%d %H:%M:%S"
        )
        end = datetime.datetime.strptime(new_event.end, "%Y-%m-%d %H:%M:%S")
        if (start.date() != end.date()) and (
            datetime.time(0, 0, 1) <= end.time()
        ):
            flash("Event ends on a different day!", "danger")
            raise DifferentDayEndError

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


class OverlappingEventError(Exception):
    pass


class EndBeforeStartError(Exception):
    pass


class DifferentDayEndError(Exception):
    pass


week_bp.add_url_rule(
    "/<int:year>/<int:week>",
    view_func=WeekView.as_view("week"),
    methods=["GET", "POST"],
)
