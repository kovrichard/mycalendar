from truth.truth import AssertThat

from tests import (
    AppTestCase,
    DbMixin,
    TemplateRenderMixin,
    TestClientMixin,
    logged_in_user,
)


class ApiTest(TestClientMixin, DbMixin, TemplateRenderMixin, AppTestCase):
    @logged_in_user
    def test_get_main_redirects_to_week_view(self):
        # with self.logged_in_user():
        r = self.client.get("/")
        template, context = self.rendered_templates[0]
        AssertThat(r.status_code).IsEqualTo(302)
        AssertThat(r.headers["Location"]).Contains("/week/")
        AssertThat(1).IsEqualTo(2)
