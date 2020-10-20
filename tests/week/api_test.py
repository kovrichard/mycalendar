from datetime import datetime

from truth.truth import AssertThat

from mycalendar.db_models.event import Event
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
        Event.query.delete()

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

    @logged_in_user("user")
    def test_get_week_post_saves_event_to_db(self, default_user):
        payload = {
            "title": "<title>",
            "description": "<description>",
            "location": "<location>",
            "start_date": "2020-10-20",
            "start_time": "00:00",
            "end_date": "2020-10-20",
            "end_time": "01:00",
            "business_hour": 1,
        }

        r = self.client.post("/week/2", data=payload)

        event = Event.query.filter_by(title="<title>").first()

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(event.title).IsEqualTo(payload["title"])
        AssertThat(event.description).IsEqualTo(payload["description"])
        AssertThat(event.location).IsEqualTo(payload["location"])
        start_string = f"{payload['start_date']} {payload['start_time']}"
        AssertThat(event.start).IsEqualTo(
            datetime.strptime(start_string, "%Y-%m-%d %H:%M")
        )
        end_string = f"{payload['end_date']} {payload['end_time']}"
        AssertThat(event.end).IsEqualTo(
            datetime.strptime(end_string, "%Y-%m-%d %H:%M")
        )
        AssertThat(event.event_type).IsEqualTo(payload["business_hour"])
