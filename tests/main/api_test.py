from truth.truth import AssertThat

from tests import AppTestCase, TemplateRenderMixin, TestClientMixin


class MainTest(TestClientMixin, TemplateRenderMixin, AppTestCase):
    def test_get_main_redirects_to_week_view(self):
        r = self.client.get("/")

        AssertThat(r.status_code).IsEqualTo(302)
        AssertThat(r.headers["Location"]).Contains("/")
