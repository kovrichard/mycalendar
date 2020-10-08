from truth.truth import AssertThat

from mycalendar.db_models.user import User
from tests import AppTestCase, DbMixin, TemplateRenderMixin, TestClientMixin


class TestApi(TestClientMixin, TemplateRenderMixin, DbMixin, AppTestCase):
    def setUp(self):
        User.query.delete()

    def test_welcome_renders_template(self):
        r = self.client.get("/")
        template, context = self.rendered_templates[0]
        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("welcome.html")

    def test_welcome_user_is_inserted(self):
        r = self.client.get("/")

        user = User.query.filter(User.username.like("mas%")).first()

        AssertThat(user.password).IsEqualTo("pw")
