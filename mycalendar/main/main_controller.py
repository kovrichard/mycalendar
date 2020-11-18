from datetime import datetime

from mycalendar.lib.datetime_helper import DateTimeHelper


class MainController:
    def __init__(self):
        self.__date_time_helper = DateTimeHelper()

    def get_current_year(self):
        return datetime.now().isocalendar()[0]

    def get_current_week(self):
        return datetime.now().isocalendar()[1]

    def get_days_of_week(self):
        return self.__date_time_helper.calculate_days_of_week(
            self.get_current_year(), self.get_current_week()
        )
