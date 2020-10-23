from truth.truth import AssertThat

from mycalendar.db_models.role import Role
from mycalendar.db_models.user import User
from mycalendar.db_models.user_roles import UserRoles
from tests import (
    AppTestCase,
    DbMixin,
    TemplateRenderMixin,
    TestClientMixin,
    logged_in_user,
)


class ApiTest(TestClientMixin, DbMixin, TemplateRenderMixin, AppTestCase):
    def setUp(self):
        super().setUp()
        UserRoles.query.delete()
        User.query.delete()
        Role.query.delete()

    @logged_in_user()
    def test_share_renders_template(self, default_user):
        r = self.client.get("/share")

        template, context = self.rendered_templates[0]

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("share.html")
