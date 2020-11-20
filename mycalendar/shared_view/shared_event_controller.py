from datetime import datetime, timedelta

from flask import current_app

from mycalendar.db_models.db_event import Event
from mycalendar.db_models.db_user import User
from mycalendar.lib.datetime_helper import DateTimeHelper
from mycalendar.lib.user_access import UserAccess


class SharedEventController:
    def __init__(self):
        self.__date_time_helper = DateTimeHelper()
        self.__token = ""
        self.__request = ""
        self.__year = ""
        self.__week = ""
        self.__day = ""
        self.__hour = ""

    def get_year(self):
        return self.__year

    def get_week(self):
        return self.__week

    def set_token(self, token):
        self.__token = token

    def set_request(self, request):
        if self.get_decoded_token():
            self.__request = request
            self.__year = int(self.__request.form["year"])
            self.__week = int(self.__request.form["week"])
            self.__day = int(self.__request.form["day"])
            self.__hour = int(self.__request.form["hour"])

    def get_decoded_token(self):
        return UserAccess(current_app.config["SHARING_TOKEN_SECRET"]).decode(
            self.__token
        )

    def get_start_date(self):
        return datetime.fromisocalendar(
            self.__year, self.__week, self.__day + 1
        ).strftime("%Y-%m-%d")

    def get_end_date(self):
        end_date = datetime.fromisocalendar(
            self.__year, self.__week, self.__day + 1
        )

        if self.__hour == 23:
            end_date += timedelta(days=1)
        end_date = end_date.strftime("%Y-%m-%d")

        return end_date

    def get_start_time(self):
        return self.__date_time_helper.hour_number_to_24_hours_format(
            str(self.__hour)
        )

    def get_end_time(self):
        return self.__date_time_helper.hour_number_to_24_hours_format(
            str(self.__hour + 1)
        )

    def get_shared_user_name(self):
        return User.query.get(self.get_decoded_token()["user_id"]).username

    def get_event(self):
        return Event.query.filter(
            Event.start <= f"{self.get_start_date()} {self.get_start_time()}",
            Event.end >= f"{self.get_end_date()} {self.get_end_time()}",
            Event.user_id == self.get_decoded_token()["user_id"],
        ).first()
