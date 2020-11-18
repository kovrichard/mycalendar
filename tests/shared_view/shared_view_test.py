from datetime import datetime, timedelta

from flask import current_app
from truth.truth import AssertThat

from mycalendar.db_models import db
from mycalendar.db_models.db_event import Event
from mycalendar.db_models.db_role import Role
from mycalendar.db_models.db_user import User
from mycalendar.db_models.db_user_roles import UserRoles
from mycalendar.db_models.db_week import Week
from mycalendar.lib.user_access import UserAccess
from tests import AppTestCase, DbMixin, TemplateRenderMixin, TestClientMixin

YEAR = 2020
WEEK = 43


class SharedViewTest(
    TestClientMixin, DbMixin, TemplateRenderMixin, AppTestCase
):
    def setUp(self):
        super().setUp()
        Event.query.delete()
        Week.query.delete()
        UserRoles.query.delete()
        User.query.delete()
        Role.query.delete()

    def test_shared_event_view_denies_access_with_wrong_token(self):
        r = self.client.post("/shared-event/<wrong_token>")

        AssertThat(r.status_code).IsEqualTo(401)

    def test_shared_event_view_renders_template(self):
        user = User(username="user", password="password")
        db.session.add(user)
        db.session.commit()

        token = UserAccess(
            current_app.config["SHARING_TOKEN_SECRET"]
        ).generate(user.id, timedelta(days=1))

        r = self.client.post(
            f"/shared-event/{token}",
            data={"year": "2020", "week": "1", "hour": "1", "day": "1"},
        )

        template, context = self.rendered_templates[0]

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("shared-event.html")
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
            f"/shared-event/{token}",
            data={"year": "2020", "week": "2", "hour": "0", "day": "0"},
        )

        template, context = self.rendered_templates[0]

        AssertThat(r.data).Contains(b'checked id="businesshour" readonly')
        AssertThat(r.data).Contains(b'placeholder="Your name here"')

    def test_register_guest_denies_access_with_wrong_token(self):
        r = self.client.post("/register-guest/<wrong_token>")

        AssertThat(r.status_code).IsEqualTo(401)

    def test_register_guest_redirects_to_week_view(self):
        user = User(username="user", password="password")
        db.session.add(user)
        db.session.commit()

        token = UserAccess(
            current_app.config["SHARING_TOKEN_SECRET"]
        ).generate(user.id, timedelta(days=1))

        r = self.client.post(
            f"/register-guest/{token}",
            data={"event-id": 1, "guest-name": ""},
        )

        now = datetime.now().isocalendar()

        AssertThat(r.status_code).IsEqualTo(302)
        AssertThat(r.headers["Location"]).IsEqualTo(
            f"http://localhost/{now[0]}/{now[1]}/shared-calendar/{token}"
        )

    def test_register_guest_saves_guest_to_event(self):
        user = User(username="user", password="password")
        db.session.add(user)

        event = Event(
            title="test_title",
            start="2020-11-07 06:00:00",
            end="2020-11-07 07:00:00",
        )
        db.session.add(event)
        db.session.commit()

        token = UserAccess(
            current_app.config["SHARING_TOKEN_SECRET"]
        ).generate(user.id, timedelta(days=1))

        guest_name = "Test Name"

        r = self.client.post(
            f"/register-guest/{token}",
            data={"event-id": event.id, "guest-name": guest_name},
        )

        AssertThat(event.guest_name).IsEqualTo(guest_name)

    def test_shared_calendar_denies_access_with_wrong_token(self):
        r = self.client.get(f"/{YEAR}/{WEEK}/shared-calendar/<wrong-token>")

        AssertThat(r.status_code).IsEqualTo(401)

    def test_shared_calendar_renders_template(self):
        user = User(username="user", password="password")
        db.session.add(user)
        db.session.commit()

        token = UserAccess(
            current_app.config["SHARING_TOKEN_SECRET"]
        ).generate(user.id, timedelta(days=1))

        r = self.client.get(f"/{YEAR}/{WEEK}/shared-calendar/{token}")
        template, context = self.rendered_templates[0]

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("shared-week.html")
        AssertThat(context["shared_calendar"]).IsTrue()
        AssertThat(context["shared_user_name"]).IsEqualTo(user.username)

        AssertThat(r.data).Contains(b'value="<"')
        AssertThat(r.data).Contains(b'value=">"')

    def test_shared_calendar_event_creation_is_disabled(self):
        user = User(username="user", password="password")
        db.session.add(user)
        db.session.commit()

        token = UserAccess(
            current_app.config["SHARING_TOKEN_SECRET"]
        ).generate(user.id, timedelta(days=1))

        r = self.client.get(f"/{YEAR}/{WEEK}/shared-calendar/{token}")
        template, context = self.rendered_templates[0]

        AssertThat(r.data).DoesNotContain(b"btn-4-5")
