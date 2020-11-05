import re
from datetime import datetime

from flask import current_app
from truth.truth import AssertThat

from mycalendar.db_models.event import Event
from mycalendar.db_models.role import Role
from mycalendar.db_models.user import User
from mycalendar.db_models.user_roles import UserRoles
from mycalendar.lib.user_access import UserAccess
from tests import (
    AppTestCase,
    DbMixin,
    TemplateRenderMixin,
    TestClientMixin,
    logged_in_user,
)


class ShareTest(TestClientMixin, DbMixin, TemplateRenderMixin, AppTestCase):
    def setUp(self):
        super().setUp()
        Event.query.delete()
        UserRoles.query.delete()
        User.query.delete()
        Role.query.delete()

    @logged_in_user()
    def test_share_renders_template(self, default_user):
        r = self.client.get("/share")

        template, context = self.rendered_templates[0]

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("share.html")

    @logged_in_user()
    def test_get_share_link_create_shareable_link_with_correct_user_id(
        self, default_user
    ):
        r = self.client.get(
            "/share/get-link",
            query_string={
                "expiration": "2020-11-12",
                "share_content": True,
            },
        )

        now = datetime.now().isocalendar()

        token = re.search(
            f"{current_app.config['CALENDAR_URL']}/{now[0]}/{now[1]}/shared-calendar/(.*)",
            r.json["token"],
        ).group(1)
        decoded_token = UserAccess(
            current_app.config["SHARING_TOKEN_SECRET"]
        ).decode(token)

        AssertThat(decoded_token["user_id"]).IsEqualTo(default_user.id)
