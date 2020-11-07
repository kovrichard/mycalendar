from datetime import datetime

from truth.truth import AssertThat

from tests import AppTestCase, TemplateRenderMixin, TestClientMixin


class MainTest(TestClientMixin, TemplateRenderMixin, AppTestCase):
    def test_get_main_redirects_to_week_view(self):
        r = self.client.get("/")

        now = datetime.now().isocalendar()

        AssertThat(r.status_code).IsEqualTo(302)
        AssertThat(r.headers["Location"]).Contains(
            f"{self.app.config['CALENDAR_URL']}/{now[0]}/{now[1]}"
        )
