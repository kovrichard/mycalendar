from datetime import datetime

from mycalendar.db_models.db_event import Event
from mycalendar.lib.datetime_helper import DateTimeHelper


class EventController:
    def __init__(self):
        self.__date_time_helper = DateTimeHelper()
        self.__request = ""
        self.__year = 0
        self.__week = 0
        self.__day = 0
        self.__hour = 0
        self.__user = ""

    def set_request(self, request):
        self.__request = request
        self.__year = int(self.__request.form["year"])
        self.__week = int(self.__request.form["week"])
        self.__day = int(self.__request.form["day"])
        self.__hour = int(self.__request.form["hour"])

    def set_user(self, user):
        self.__user = user

    def get_year(self):
        return self.__year

    def get_week(self):
        return self.__week

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

    def get_event(self):
        return Event.query.filter(
            Event.start <= f"{self.get_start_date()} {self.get_start_time()}",
            Event.end >= f"{self.get_end_date()} {self.get_end_time()}",
            Event.user_id == self.__user.id,
        ).first()
