from datetime import datetime

from truth.truth import AssertThat

from tests import AppTestCase


class TestFactory(AppTestCase):
    def test_create_app_sets_current_year(self):
        AssertThat(self.app.jinja_env.globals["current_year"]).IsEqualTo(
            datetime.today().year
        )
