from truth.truth import AssertThat

from mycalendar.db_models.user import User
from tests import AppTestCase, TemplateRenderMixin, TestClientMixin, DbMixin, logged_in_user


class ApiTest(TestClientMixin, DbMixin, TemplateRenderMixin, AppTestCase):
    @logged_in_user
    def test_welcome_renders_template(self):
        # with self.logged_in_user():
        r = self.client.get("/")
        template, context = self.rendered_templates[0]
        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("welcome.html")
