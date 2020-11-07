from datetime import datetime, timedelta

from flask import current_app
from truth.truth import AssertThat

from mycalendar.db_models import db
from mycalendar.db_models.event import Event
from mycalendar.db_models.role import Role
from mycalendar.db_models.user import User
from mycalendar.db_models.user_roles import UserRoles
from mycalendar.db_models.week import Week
from mycalendar.lib.user_access import UserAccess
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
    def test_event_mod_renders_template(self, default_user):
        r = self.client.post(
            "/add-event",
            data={"year": "2020", "week": "1", "hour": "1", "day": "1"},
        )

        template, context = self.rendered_templates[0]

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("event-modification.html")
        AssertThat(context["start_date"]).IsEqualTo(
            datetime.fromisocalendar(2020, 1, 2).strftime("%Y-%m-%d")
        )
        AssertThat(context["start_time"]).IsEqualTo("01:00")
        AssertThat(context["end_time"]).IsEqualTo("02:00")
        AssertThat(r.data).DoesNotContain(b'placeholder="Title" readonly')
        AssertThat(r.data).DoesNotContain(
            b'placeholder="Description" readonly'
        )
        AssertThat(r.data).DoesNotContain(b'placeholder="Location" readonly')
        AssertThat(r.data).DoesNotContain(b'id="start_date" readonly')
        AssertThat(r.data).DoesNotContain(b'id="start_time" readonly')
        AssertThat(r.data).DoesNotContain(b'id="end_date" readonly')
        AssertThat(r.data).DoesNotContain(b'id="end_time" readonly')
        AssertThat(r.data).DoesNotContain(
            b'onclick="return false;" name="business_hour"'
        )
        AssertThat(r.data).Contains(b'value="Save"')
        AssertThat(r.data).Contains(b'value="Delete"')

    def test_event_mod_loads_already_defined_event(self):
        with self.logged_in_user() as user:
            event = Event(
                event_type=1,
                title="<title>",
                description="<desc>",
                location="<loc>",
                start="2020-10-19 00:00:00",
                end="2020-10-19 01:00:00",
                user_id=user.id,
            )

            db.session.add(event)
            db.session.commit()

            r = self.client.post(
                "/add-event",
                data={"year": "2020", "week": "43", "hour": "0", "day": "0"},
            )

            AssertThat(r.status_code).IsEqualTo(200)
            template, context = self.rendered_templates[0]

            AssertThat(context["event_type"]).IsEqualTo(event.event_type)
            AssertThat(context["title"]).IsEqualTo(event.title)
            AssertThat(context["description"]).IsEqualTo(event.description)
            AssertThat(context["location"]).IsEqualTo(event.location)
            AssertThat(context["start_date"]).IsEqualTo(event.start.date())
            AssertThat(context["start_time"]).IsEqualTo(event.start.time())
            AssertThat(context["end_date"]).IsEqualTo(event.end.date())
            AssertThat(context["end_time"]).IsEqualTo(event.end.time())

    @logged_in_user()
    def test_event_modification_does_not_render_events_of_other_users(
        self, default_user
    ):
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

        AssertThat(context["title"]).IsEqualTo("")

    def test_shared_event_view_denies_access_with_wrong_token(self):
        r = self.client.post("/add-event/<wrong_token>")

        AssertThat(r.status_code).IsEqualTo(401)

    def test_shared_event_view_renders_template(self):
        user = User(username="user", password="password")
        db.session.add(user)
        db.session.commit()

        token = UserAccess(
            current_app.config["SHARING_TOKEN_SECRET"]
        ).generate(user.id, timedelta(days=1))

        r = self.client.post(
            f"/add-event/{token}",
            data={"year": "2020", "week": "1", "hour": "1", "day": "1"},
        )

        template, context = self.rendered_templates[0]

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("event-modification.html")
        AssertThat(context["shared_calendar"]).IsTrue()
        AssertThat(context["shared_user_name"]).IsEqualTo(user.username)
        AssertThat(r.data).Contains(b'placeholder="Title" readonly')
        AssertThat(r.data).Contains(b'placeholder="Description" readonly')
        AssertThat(r.data).Contains(b'placeholder="Location" readonly')
        AssertThat(r.data).Contains(b'id="start_date" readonly')
        AssertThat(r.data).Contains(b'id="start_time" readonly')
        AssertThat(r.data).Contains(b'id="end_date" readonly')
        AssertThat(r.data).Contains(b'id="end_time" readonly')
        AssertThat(r.data).Contains(
            b'onclick="return false;" name="business_hour"'
        )
        AssertThat(r.data).Contains(b'value="OK"')

    @logged_in_user()
    def test_event_mod_does_not_render_guest_registration(self, default_user):
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
        AssertThat(r.data).DoesNotContain(b'placeholder="Your name here"')

    def test_shared_event_view_renders_guest_registration(self):
        user = User(username="user", password="password")
        db.session.add(user)
        db.session.commit()

        token = UserAccess(
            current_app.config["SHARING_TOKEN_SECRET"]
        ).generate(user.id, timedelta(days=1))

        week = Week(year=2020, week_num=2)
        db.session.add(week)
        event = Event(
            event_type=1,
            title="test_event",
            start="2020-01-06 00:00:00",
            end="2020-01-06 01:00:00",
            week_id=week.id,
            user_id=user.id,
        )
        db.session.add(event)
        db.session.commit()

        r = self.client.post(
            f"/add-event/{token}",
            data={"year": "2020", "week": "2", "hour": "0", "day": "0"},
        )

        template, context = self.rendered_templates[0]

        AssertThat(r.data).Contains(b'checked id="businesshour" readonly')
        AssertThat(r.data).Contains(b'placeholder="Your name here"')

    def test_register_guest_denies_access_with_wrong_token(self):
        r = self.client.post("/add-event/register-guest/<wrong_token>")

        AssertThat(r.status_code).IsEqualTo(401)

    def test_register_guest_redirects_to_week_view(self):
        user = User(username="user", password="password")
        db.session.add(user)
        db.session.commit()

        token = UserAccess(
            current_app.config["SHARING_TOKEN_SECRET"]
        ).generate(user.id, timedelta(days=1))

        r = self.client.post(
            f"/add-event/register-guest/{token}", data={"event-id": 1}
        )

        now = datetime.now().isocalendar()

        AssertThat(r.status_code).IsEqualTo(302)
        AssertThat(r.headers["Location"]).IsEqualTo(
            f"{self.app.config['CALENDAR_URL']}/{now[0]}/{now[1]}/shared-calendar/{token}"
        )
