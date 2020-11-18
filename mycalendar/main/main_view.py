from flask import Blueprint, redirect, url_for
from flask.views import MethodView

from .main_controller import MainController

main_bp = Blueprint("main", __name__, template_folder="templates")


class MainView(MethodView):
    def __init__(self):
        self.__main_controller = MainController()

    def get(self):
        return redirect(
            url_for(
                "week.week",
                year=self.__main_controller.get_current_year(),
                week=self.__main_controller.get_current_week(),
                days_of_week=self.__main_controller.get_days_of_week(),
            ),
            302,
        )


main_bp.add_url_rule("/", view_func=MainView.as_view("main"), methods=["GET"])
