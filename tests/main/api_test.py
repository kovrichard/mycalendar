from truth.truth import AssertThat

from mycalendar.db_models import session
from mycalendar.db_models.user import User
from tests import AppTestCase, TemplateRenderMixin, TestClientMixin


class TestApi(TestClientMixin, TemplateRenderMixin, AppTestCase):
    def setUp(self):
        session.query(User).delete()

    def test_welcome_renders_template(self):
        r = self.client.get("/")
        template, context = self.rendered_templates[0]
        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("welcome.html")

    def test_welcome_get_or_works(self):
        r = self.client.get("/")

        user = session.query(User).get_or(10, 1)

        AssertThat(user).IsEqualTo(1)
