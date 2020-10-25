from datetime import datetime

from ddt import data, ddt, unpack
from truth.truth import AssertThat

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
WEEK = 2

TEST_EVENT = {
    "title": "<title>",
    "description": "<description>",
    "location": "<location>",
    "start_date": "2020-10-20",
    "start_time": "00:00",
    "end_date": "2020-10-20",
    "end_time": "01:00",
    "business_hour": 1,
}


@ddt
class WeekTest(TestClientMixin, DbMixin, TemplateRenderMixin, AppTestCase):
    def setUp(self):
        super().setUp()
        Event.query.delete()
        Week.query.delete()
        UserRoles.query.delete()
        User.query.delete()
        Role.query.delete()

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

    @data(
        (2020, 0),
        (2020, 52),
        (2020, 53),
        (2020, 54),
        (2021, 0),
        (2021, 52),
        (2021, 53),
        (2021, 54),
        (datetime.now().isocalendar()[0], datetime.now().isocalendar()[1]),
    )
    @unpack
    @logged_in_user()
    def test_get_week_handles_anniversaries_correctly(
        self, year, week, default_user
    ):
        r = self.client.get(f"/{year}/{week}")

        AssertThat(r.status_code).IsEqualTo(200)

    @logged_in_user()
    def test_get_week_get_persists_week_into_db(self, default_user):
        r = self.client.get(f"/{YEAR}/{WEEK}")

        week = Week.query.filter_by(year=YEAR, week_num=WEEK).first()

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(week.year).IsEqualTo(YEAR)
        AssertThat(week.week_num).IsEqualTo(WEEK)

    @logged_in_user()
    def test_get_week_get_does_not_save_already_existing_event_again(
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
            self.client.get(f"/{YEAR}/{WEEK}")

            r = self.client.post(f"/{YEAR}/{WEEK}", data=TEST_EVENT)

            AssertThat(r.status_code).IsEqualTo(200)
            event = Event.query.filter_by(title="<title>").first()

            AssertThat(event.title).IsEqualTo(TEST_EVENT["title"])
            AssertThat(event.description).IsEqualTo(TEST_EVENT["description"])
            AssertThat(event.location).IsEqualTo(TEST_EVENT["location"])
            start_string = (
                f"{TEST_EVENT['start_date']} {TEST_EVENT['start_time']}"
            )
            AssertThat(event.start).IsEqualTo(
                datetime.strptime(start_string, "%Y-%m-%d %H:%M")
            )
            end_string = f"{TEST_EVENT['end_date']} {TEST_EVENT['end_time']}"
            AssertThat(event.end).IsEqualTo(
                datetime.strptime(end_string, "%Y-%m-%d %H:%M")
            )
            AssertThat(event.event_type).IsEqualTo(TEST_EVENT["business_hour"])

            week = Week.query.filter_by(year=YEAR, week_num=WEEK).first()

            AssertThat(len(week.events)).IsEqualTo(1)
            AssertThat(week.events[0].title).IsEqualTo(TEST_EVENT["title"])

            AssertThat(week.events[0].user_id).IsEqualTo(user.id)
