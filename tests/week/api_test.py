from datetime import datetime

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


class WeekTest(TestClientMixin, DbMixin, TemplateRenderMixin, AppTestCase):
    def setUp(self):
        super().setUp()
        UserRoles.query.delete()
        User.query.delete()
        Role.query.delete()

    @logged_in_user("user")
    def test_get_week_renders_week_template(self, default_user):
        week_num = 2
        r = self.client.get(f"/week/{week_num}")

        template, context = self.rendered_templates[0]

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("week.html")
        AssertThat(context["week_number"]).IsEqualTo(week_num)
        AssertThat(context["current_week"]).IsEqualTo(
            datetime.now().isocalendar()[1]
        )
