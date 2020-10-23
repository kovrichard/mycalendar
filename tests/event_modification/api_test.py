from datetime import datetime

from truth.truth import AssertThat

from mycalendar.db_models import db
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


class EventModificationTest(
    TestClientMixin, DbMixin, TemplateRenderMixin, AppTestCase
):
    def setUp(self):
        super().setUp()
        Event.query.delete()
        UserRoles.query.delete()
        User.query.delete()
        Role.query.delete()

    @logged_in_user()
    def test_event_mod_renders_template(self, default_user):
        r = self.client.post(
            "/add-event", data={"week_num": "1", "n": "1", "m": "1"}
        )

        template, context = self.rendered_templates[0]

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("event-modification.html")
        AssertThat(context["start_date"]).IsEqualTo(
            datetime.fromisocalendar(2020, 1, 2).strftime("%Y-%m-%d")
        )
        AssertThat(context["start_time"]).IsEqualTo("01:00")
        AssertThat(context["end_time"]).IsEqualTo("02:00")

    @logged_in_user()
    def test_event_mod_loads_already_defined_event(self, default_user):
        event = Event(
            title="<title>",
            description="<desc>",
            location="<loc>",
            start="2020-10-19 00:00:00",
            end="2020-10-19 01:00:00",
        )
        db.session.add(event)
        db.session.commit()

        r = self.client.post(
            "/add-event", data={"week_num": "43", "n": "0", "m": "0"}
        )

        AssertThat(r.status_code).IsEqualTo(200)
        template, context = self.rendered_templates[0]

        AssertThat(context["title"]).IsEqualTo(event.title)
        AssertThat(context["description"]).IsEqualTo(event.description)
        AssertThat(context["location"]).IsEqualTo(event.location)
        AssertThat(context["start_date"]).IsEqualTo(event.start.date())
        AssertThat(context["start_time"]).IsEqualTo(event.start.time())
        AssertThat(context["end_date"]).IsEqualTo(event.end.date())
        AssertThat(context["end_time"]).IsEqualTo(event.end.time())
