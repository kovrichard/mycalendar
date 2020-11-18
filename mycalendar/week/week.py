import datetime

from flask import Blueprint, flash, render_template, request
from flask.views import MethodView
from flask_user import current_user, login_required

from mycalendar.db_models import db
from mycalendar.db_models.db_event import Event
from mycalendar.db_models.db_week import Week
from mycalendar.lib.datetime_helper import DateTimeHelper

week_bp = Blueprint("week", __name__, template_folder="templates")

date_time_helper = DateTimeHelper()


class WeekAPI(MethodView):
    @login_required
    def get(self, year, week):
        current_week = self.__persist_week_to_db(year, week)
        days_of_week = date_time_helper.calculate_days_of_week(year, week)

        events = Event.query.filter_by(
            week_id=current_week.id, user_id=current_user.id
        ).all()

        return render_template(
            "week.html",
            year_number=year,
            week_number=week,
            days_of_week=days_of_week,
            events=self.__format_for_render(events),
        )

    @login_required
    def post(self, year, week):
        event_type = 1 if "business_hour" in request.form else 0

        if current_week := Week.query.filter_by(
            year=year, week_num=week
        ).first():
            event = Event.query.filter_by(id=request.form["event-id"]).first()

            if request.form["action"] == "Save":
                if event:
                    new_event = self.__modify_event(event, event_type)
                else:
                    new_event = self.__insert_new_event(
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

            elif event:
                self.__delete_event(event)

        days_of_week = date_time_helper.calculate_days_of_week(year, week)

        events = Event.query.filter_by(
            week_id=current_week.id, user_id=current_user.id
        ).all()

        return render_template(
            "week.html",
            year_number=year,
            week_number=week,
            days_of_week=days_of_week,
            events=self.__format_for_render(events),
        )

    def __persist_week_to_db(self, year, week):
        tmp = Week.query.filter_by(year=year, week_num=week).first()

        if tmp is None:
            tmp = Week(year=year, week_num=week)
            db.session.add(tmp)
            db.session.commit()

        return tmp

    def __delete_event(self, event):
        Event.query.filter_by(
            start=event.start, end=event.end, user_id=event.user_id
        ).delete()
        db.session.commit()

    def __modify_event(self, event, event_type):
        event.title = request.form["title"]
        event.description = request.form["description"]
        event.location = request.form["location"]
        event.start = (
            f"{request.form['start_date']} {request.form['start_time']}"
        )
        event.end = f"{request.form['end_date']} {request.form['end_time']}"
        event.event_type = event_type
        event.guest_name = (
            request.form["guest-name"] if event_type == 1 else ""
        )

        return event

    def __insert_new_event(self, current_week, event_type):
        event = Event(
            title=request.form["title"],
            description=request.form["description"],
            location=request.form["location"],
            start=f"{request.form['start_date']} {request.form['start_time']}",
            end=f"{request.form['end_date']} {request.form['end_time']}",
            event_type=event_type,
            guest_name=request.form["guest-name"] if event_type == 1 else "",
        )
        db.session.add(event)

        current_week.events.append(event)
        current_user.events.append(event)

        return event

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
    view_func=WeekAPI.as_view("week"),
    methods=["GET", "POST"],
)
