import re
from datetime import datetime, timedelta

from flask import current_app
from truth.truth import AssertThat

from mycalendar.db_models.db_event import Event
from mycalendar.db_models.db_role import Role
from mycalendar.db_models.db_user import User
from mycalendar.db_models.db_user_roles import UserRoles
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
    def test_get_share_link_creates_shareable_link_correctly(
        self, default_user
    ):
        r = self.client.get(
            "/get-share-link",
            query_string={
                "expiration": (datetime.now() + timedelta(days=7)).strftime(
                    "%Y-%m-%d"
                ),
                "share-content": "true",
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
        AssertThat(decoded_token["share_content"]).IsTrue()
