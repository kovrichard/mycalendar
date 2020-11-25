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
        self.new_event = ""

    def set_current_user(self, current_user):
        self.__current_user = current_user

    def set_year_and_week(self, year, week):
        y, w = self.__date_time_helper.calculate_different_year(year, week)

        self.__year = y
        self.__week = w
        self.__persist_week_to_db()

    def get_week(self):
        return self.__week

    def get_year(self):
        return self.__year

    def set_request(self, request):
        self.__request = request

    def get_current_week(self):
        return Week.query.filter_by(
            year=self.__year, week_num=self.__week
        ).first()

    def get_new_event(self):
        return self.new_event

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
            item["type"] = (
                "active-normal-event"
                if e.event_type == 0
                else "active-business-event"
            )

            tmp.append(item)

        return tmp

    def handle_post_request(self):
        event = Event.query.filter_by(
            id=self.__request.form["event-id"]
        ).first()

        if self.__request.form["action"] == "Save":
            self.new_event = self.save_event(event)

            try:
                self.check_event(self.new_event)
                db.session.commit()
            except OverlappingEventError:
                db.session.rollback()
                raise
            except EndBeforeStartError:
                db.session.rollback()
                raise
            except DifferentDayEndError:
                db.session.rollback()
                raise
            except ShortEventError:
                db.session.rollback()
                raise
        else:
            self.delete_event(event)

    def save_event(self, event):
        if event:
            new_event = self.modify_event(
                event, self.get_event_type_from_request()
            )
        else:
            new_event = self.insert_new_event(
                self.get_current_week(), self.get_event_type_from_request()
            )
        return new_event

    def insert_new_event(self, current_week, event_type):
        start_time = self.__format_time(self.__request.form["start_time"])
        end_time = self.__format_time(self.__request.form["end_time"])

        event = Event(
            title=self.__request.form["title"],
            description=self.__request.form["description"],
            location=self.__request.form["location"],
            start=f"{self.__request.form['start_date']} {start_time}",
            end=f"{self.__request.form['end_date']} {end_time}",
            event_type=event_type,
            guest_name=self.__request.form["guest-name"]
            if event_type == 1
            else "",
        )
        db.session.add(event)

        current_week.events.append(event)
        self.__current_user.events.append(event)

        return event

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

    def check_event(self, new_event):
        self.__overlapping_event(new_event)
        self.__event_end_is_earlier_than_start(new_event)
        self.__event_ends_on_different_day(new_event)
        self.__event_is_shorter_than_one_hour(new_event)

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
            raise OverlappingEventError

    def __event_end_is_earlier_than_start(self, new_event):
        if new_event.end <= new_event.start:

            raise EndBeforeStartError

    def __event_ends_on_different_day(self, new_event):
        start = datetime.datetime.strptime(
            new_event.start, "%Y-%m-%d %H:%M:%S"
        )
        end = datetime.datetime.strptime(new_event.end, "%Y-%m-%d %H:%M:%S")
        if (start.date() != end.date()) and (
            datetime.time(0, 0, 1) <= end.time()
        ):
            raise DifferentDayEndError

    def __event_is_shorter_than_one_hour(self, new_event):
        start = datetime.datetime.strptime(
            new_event.start, "%Y-%m-%d %H:%M:%S"
        )
        end = datetime.datetime.strptime(new_event.end, "%Y-%m-%d %H:%M:%S")

        if (end - start) < datetime.timedelta(hours=1):
            raise ShortEventError


class OverlappingEventError(Exception):
    pass


class EndBeforeStartError(Exception):
    pass


class DifferentDayEndError(Exception):
    pass


class ShortEventError(Exception):
    pass
