import datetime

from mycalendar.db_models import db
from mycalendar.db_models.db_event import Event
from mycalendar.db_models.db_week import Week
from mycalendar.lib.datetime_helper import DateTimeHelper


class WeekController:
    def __init__(self):
        self.__date_time_helper = DateTimeHelper()
        self.__current_user = ""
        self.__week = ""
        self.__year = ""
        self.__request = ""

    def set_current_user(self, current_user):
        self.__current_user = current_user

    def set_year(self, year):
        self.__year = year

    def set_week(self, week):
        self.__week = week
        self.__persist_week_to_db()

    def set_request(self, request):
        self.__request = request

    def get_current_week(self):
        return Week.query.filter_by(
            year=self.__year, week_num=self.__week
        ).first()

    def get_days_of_week(self):
        return self.__date_time_helper.calculate_days_of_week(
            self.__year, self.__week
        )

    def get_formatted_events(self):
        events = Event.query.filter_by(
            week_id=self.get_current_week().id, user_id=self.__current_user.id
        ).all()

        return self.__format_for_render(events)

    def get_event_type_from_request(self):
        return 1 if "business_hour" in self.__request.form else 0

    def __persist_week_to_db(self):
        tmp = Week.query.filter_by(
            year=self.__year, week_num=self.__week
        ).first()

        if tmp is None:
            tmp = Week(year=self.__year, week_num=self.__week)
            db.session.add(tmp)
            db.session.commit()

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

    def modify_event(self, event, event_type):
        start_time = self.__format_time(self.__request.form["start_time"])
        end_time = self.__format_time(self.__request.form["end_time"])

        event.title = self.__request.form["title"]
        event.description = self.__request.form["description"]
        event.location = self.__request.form["location"]
        event.start = f"{self.__request.form['start_date']} {start_time}"
        event.end = f"{self.__request.form['end_date']} {end_time}"
        event.event_type = event_type
        event.guest_name = (
            self.__request.form["guest-name"] if event_type == 1 else ""
        )

        return event

    def delete_event(self, event):
        if event:
            Event.query.filter_by(
                start=event.start, end=event.end, user_id=event.user_id
            ).delete()
            db.session.commit()

    def __format_time(self, time_string):
        try:
            datetime.datetime.strptime(time_string, "%H:%M:%S")
            return time_string
        except ValueError:
            return f"{time_string}:00"
