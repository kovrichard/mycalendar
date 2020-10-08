from truth.truth import AssertThat

from tests import AppTestCase, TemplateRenderMixin, TestClientMixin, DbMixin

from mycalendar.db_models.user import User


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

        user = User.query.filter_by(username="mas").first()

        AssertThat(user.password).IsEqualTo("pw")
