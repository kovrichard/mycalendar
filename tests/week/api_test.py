from datetime import datetime

from truth.truth import AssertThat

from mycalendar.db_models import db
from mycalendar.db_models.event import Event
from mycalendar.db_models.role import Role
from mycalendar.db_models.user import User
from mycalendar.db_models.user_roles import UserRoles
from mycalendar.db_models.week import Week
from tests import (
    AppTestCase,
    DbMixin,
    TemplateRenderMixin,
    TestClientMixin,
    logged_in_user,
)

YEAR = 2020
WEEK = 43

TEST_EVENT = {
    "title": "test_title",
    "description": "test_description",
    "location": "test_location",
    "start_date": "2020-10-20",
    "start_time": "00:00",
    "end_date": "2020-10-20",
    "end_time": "01:00",
    "business_hour": 1,
    "action": "Save",
}

TEST_DELETE_EVENT = {
    "title": "test_title",
    "description": "test_description",
    "location": "test_location",
    "start_date": "2020-10-20",
    "start_time": "00:00",
    "end_date": "2020-10-20",
    "end_time": "01:00",
    "business_hour": 1,
    "action": "Delete",
}


class WeekTest(TestClientMixin, DbMixin, TemplateRenderMixin, AppTestCase):
    def setUp(self):
        super().setUp()
        Event.query.delete()
        Week.query.delete()
        UserRoles.query.delete()
        User.query.delete()
        Role.query.delete()

        week = Week(year=YEAR, week_num=WEEK)
        db.session.add(week)
        db.session.commit()

    @logged_in_user()
    def test_get_week_renders_week_template(self, default_user):
        r = self.client.get(f"/{YEAR}/{WEEK}")

        template, context = self.rendered_templates[0]

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("week.html")
        AssertThat(context["year_number"]).IsEqualTo(YEAR)
        AssertThat(context["week_number"]).IsEqualTo(WEEK)

        for i in range(1, 8):
            AssertThat(context["days_of_week"][i - 1]["date"]).IsEqualTo(
                datetime.fromisocalendar(YEAR, WEEK, i).date()
            )
            AssertThat(context["days_of_week"][i - 1]["name"]).IsEqualTo(
                datetime.fromisocalendar(YEAR, WEEK, i).date().strftime("%A")
            )

    @logged_in_user()
    def test_get_week_post_renders_week_template(self, default_user):
        r = self.client.post(f"/{YEAR}/{WEEK}", data=TEST_EVENT)

        template, context = self.rendered_templates[0]

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("week.html")
        AssertThat(context["year_number"]).IsEqualTo(YEAR)
        AssertThat(context["week_number"]).IsEqualTo(WEEK)

        for i in range(1, 8):
            AssertThat(context["days_of_week"][i - 1]["date"]).IsEqualTo(
                datetime.fromisocalendar(YEAR, WEEK, i).date()
            )
            AssertThat(context["days_of_week"][i - 1]["name"]).IsEqualTo(
                datetime.fromisocalendar(YEAR, WEEK, i).date().strftime("%A")
            )

    @logged_in_user()
    def test_get_week_get_persists_week_into_db(self, default_user):
        r = self.client.get(f"/{YEAR}/{WEEK}")

        week = Week.query.filter_by(year=YEAR, week_num=WEEK).first()

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(week.year).IsEqualTo(YEAR)
        AssertThat(week.week_num).IsEqualTo(WEEK)

    @logged_in_user()
    def test_get_week_get_does_not_save_already_existing_week_again(
        self, default_user
    ):
        r = self.client.get(f"/{YEAR}/{WEEK}")
        r2 = self.client.get(f"/{YEAR}/{WEEK}")

        weeks = Week.query.filter_by(year=YEAR, week_num=WEEK).all()

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(r2.status_code).IsEqualTo(200)
        AssertThat(len(weeks)).IsEqualTo(1)

    def test_get_week_post_saves_event_to_db(self):
        with self.logged_in_user() as user:
            r = self.client.post(f"/{YEAR}/{WEEK}", data=TEST_EVENT)

            AssertThat(r.status_code).IsEqualTo(200)
            event = Event.query.filter_by(title=TEST_EVENT["title"]).first()

            AssertThat(event.title).IsEqualTo(TEST_EVENT["title"])
            AssertThat(event.description).IsEqualTo(TEST_EVENT["description"])
            AssertThat(event.location).IsEqualTo(TEST_EVENT["location"])
            AssertThat(event.start).IsEqualTo(
                datetime.strptime(
                    f"{TEST_EVENT['start_date']} {TEST_EVENT['start_time']}",
                    "%Y-%m-%d %H:%M",
                )
            )
            AssertThat(event.end).IsEqualTo(
                datetime.strptime(
                    f"{TEST_EVENT['end_date']} {TEST_EVENT['end_time']}",
                    "%Y-%m-%d %H:%M",
                )
            )
            AssertThat(event.event_type).IsEqualTo(TEST_EVENT["business_hour"])

            week = Week.query.filter_by(year=YEAR, week_num=WEEK).first()

            AssertThat(len(week.events)).IsEqualTo(1)
            AssertThat(week.events[0].title).IsEqualTo(TEST_EVENT["title"])

            AssertThat(week.events[0].user_id).IsEqualTo(user.id)

    @logged_in_user()
    def test_get_week_post_does_not_save_event_on_delete(self, default_user):
        r = self.client.post(f"/{YEAR}/{WEEK}", data=TEST_DELETE_EVENT)

        AssertThat(r.status_code).IsEqualTo(200)
        event = Event.query.filter_by(title="<title>").first()

        AssertThat(event).IsEqualTo(None)

    @logged_in_user()
    def test_get_week_shows_saved_events(self, default_user):
        r = self.client.post(f"/{YEAR}/{WEEK}", data=TEST_EVENT)

        template, context = self.rendered_templates[0]

        AssertThat(r.data).Contains(TEST_EVENT["title"].encode())
