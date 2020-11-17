from datetime import datetime

from truth.truth import AssertThat

from mycalendar.db_models import db
from mycalendar.db_models.db_event import Event
from mycalendar.db_models.db_role import Role
from mycalendar.db_models.db_user import User
from mycalendar.db_models.db_user_roles import UserRoles
from mycalendar.db_models.db_week import Week
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
        Week.query.delete()
        UserRoles.query.delete()
        User.query.delete()
        Role.query.delete()

    @logged_in_user()
    def test_event_renders_template(self, default_user):
        r = self.client.post(
            "/add-event",
            data={"year": "2020", "week": "1", "hour": "1", "day": "1"},
        )

        template, context = self.rendered_templates[0]

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("event.html")
        AssertThat(context["start_date"]).IsEqualTo(
            datetime.fromisocalendar(2020, 1, 2).strftime("%Y-%m-%d")
        )
        AssertThat(context["start_time"]).IsEqualTo("01:00:00")
        AssertThat(context["end_time"]).IsEqualTo("02:00:00")
        AssertThat(r.data).DoesNotContain(b'placeholder="Title" readonly')
        AssertThat(r.data).DoesNotContain(
            b'placeholder="Description" readonly'
        )
        AssertThat(r.data).DoesNotContain(b'placeholder="Location" readonly')
        AssertThat(r.data).Contains(b'id="start_date" readonly')
        AssertThat(r.data).DoesNotContain(b'id="start_time" readonly')
        AssertThat(r.data).Contains(b'id="end_date" readonly')
        AssertThat(r.data).DoesNotContain(b'id="end_time" readonly')
        AssertThat(r.data).DoesNotContain(
            b'onclick="return false;" name="business_hour"'
        )
        AssertThat(r.data).Contains(b'value="Save"')
        AssertThat(r.data).Contains(b'value="Delete"')

    @logged_in_user()
    def test_event_loads_already_defined_event(self, default_user):
        event = Event(
            event_type=1,
            title="<title>",
            description="<desc>",
            location="<loc>",
            start="2020-10-19 00:00:00",
            end="2020-10-19 01:00:00",
            user_id=default_user.id,
            guest_name="<guest>",
        )

        db.session.add(event)
        db.session.commit()

        r = self.client.post(
            "/add-event",
            data={"year": "2020", "week": "43", "hour": "0", "day": "0"},
        )

        AssertThat(r.status_code).IsEqualTo(200)
        template, context = self.rendered_templates[0]

        AssertThat(context["event"].event_type).IsEqualTo(event.event_type)
        AssertThat(context["event"].title).IsEqualTo(event.title)
        AssertThat(context["event"].description).IsEqualTo(event.description)
        AssertThat(context["event"].location).IsEqualTo(event.location)
        AssertThat(context["start_date"]).IsEqualTo(event.start.date())
        AssertThat(context["start_time"]).IsEqualTo(event.start.time())
        AssertThat(context["end_date"]).IsEqualTo(event.end.date())
        AssertThat(context["end_time"]).IsEqualTo(event.end.time())
        AssertThat(context["event"].guest_name).IsEqualTo(event.guest_name)

    @logged_in_user()
    def test_event_does_not_render_events_of_other_users(self, default_user):
        user2 = User(username="username", password="password")
        db.session.add(user2)

        event = Event(
            event_type=1,
            title="<title>",
            description="<desc>",
            location="<loc>",
            start="2020-10-20 00:00:00",
            end="2020-10-20 01:00:00",
            user_id=user2.id,
        )

        db.session.add(event)
        db.session.commit()

        r = self.client.post(
            "/add-event",
            data={"year": "2020", "week": "43", "hour": "0", "day": "1"},
        )

        AssertThat(r.status_code).IsEqualTo(200)
        template, context = self.rendered_templates[0]

        AssertThat(context["event"]).IsEqualTo(None)

    @logged_in_user()
    def test_event_does_not_render_guest_registration(self, default_user):
        week = Week(year=2020, week_num=2)
        db.session.add(week)
        event = Event(
            event_type=1,
            title="test_event",
            start="2020-01-06 00:00:00",
            end="2020-01-06 01:00:00",
            week_id=week.id,
            user_id=default_user.id,
        )
        db.session.add(event)
        db.session.commit()

        r = self.client.post(
            "/add-event",
            data={"year": "2020", "week": "2", "hour": "0", "day": "0"},
        )

        template, context = self.rendered_templates[0]

        AssertThat(r.data).Contains(b'checked id="businesshour"')
        AssertThat(r.data).Contains(b'placeholder="Guest name here"')
