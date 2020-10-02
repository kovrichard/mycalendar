import os
from datetime import datetime
from unittest import TestCase

from truth.truth import AssertThat

from mycalendar.server.factory import create_app


class TestFactory(TestCase):
    def test_create_app_sets_current_year(self):
        app = create_app()

        AssertThat(app.jinja_env.globals["current_year"]).IsEqualTo(
            datetime.today().year
        )

    def test_create_app_database_url_is_set(self):
        app = create_app()

        AssertThat(app.config["DB_URL"]).IsEqualTo(os.environ.get("TEST_DB_URL"))

    def test_create_app_config_can_be_set_from_outside(self):
        app = create_app({"<KEY>": "<VALUE>"})

        AssertThat(app.config["<KEY>"]).IsEqualTo("<VALUE>")
