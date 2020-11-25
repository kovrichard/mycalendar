from flask import current_app

from mycalendar.db_models import db
from mycalendar.db_models.db_event import Event
from mycalendar.db_models.db_user import User
from mycalendar.db_models.db_week import Week
from mycalendar.lib.datetime_helper import DateTimeHelper
from mycalendar.lib.user_access import UserAccess


class SharedWeekController:
    def __init__(self):
        self.__date_time_helper = DateTimeHelper()
        self.__year = ""
        self.__week = ""
        self.__token = ""

    def set_year_and_week(self, year, week):
        y, w = self.__date_time_helper.calculate_different_year(year, week)

        self.__year = y
        self.__week = w
        self.__persist_week_to_db()

    def set_token(self, token):
        self.__token = token

    def get_week(self):
        return self.__week

    def get_year(self):
        return self.__year

    def get_decoded_token(self):
        return UserAccess(current_app.config["SHARING_TOKEN_SECRET"]).decode(
            self.__token
        )

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
            week_id=self.get_current_week().id,
            user_id=self.get_decoded_token()["user_id"],
        ).all()

        return self.__format_for_render(events)

    def get_shared_user_name(self):
        return User.query.get(self.get_decoded_token()["user_id"]).username

    def get_share_content(self):
        return self.get_decoded_token()["share_content"]

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
