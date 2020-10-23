from datetime import datetime
from unittest import TestCase

from truth.truth import AssertThat

from mycalendar.server.factory import create_app


class FactoryTest(TestCase):
    def test_create_app_sets_current_year(self):
        app = create_app()

        AssertThat(app.jinja_env.globals["current_year"]).IsEqualTo(
            datetime.today().year
        )

    def test_create_app_config_can_be_set_from_outside(self):
        app = create_app({"<KEY>": "<VALUE>"})

        AssertThat(app.config["<KEY>"]).IsEqualTo("<VALUE>")
