from datetime import datetime, timedelta

from ddt import data, ddt, unpack
from flask import current_app
from truth.truth import AssertThat

from mycalendar.db_models import db
from mycalendar.db_models.db_event import Event
from mycalendar.db_models.db_role import Role
from mycalendar.db_models.db_user import User
from mycalendar.db_models.db_user_roles import UserRoles
from mycalendar.db_models.db_week import Week
from mycalendar.lib.user_access import UserAccess
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
    "event-id": -1,
    "title": "test_title",
    "description": "test_description",
    "location": "test_location",
    "start_date": "2020-10-20",
    "start_time": "02:00:00",
    "end_date": "2020-10-20",
    "end_time": "03:00:00",
    "business_hour": 1,
    "action": "Save",
    "guest-name": "",
}

TEST_DELETE_EVENT = {
    "event-id": -1,
    "title": "test_title",
    "description": "test_description",
    "location": "test_location",
    "start_date": "2020-10-20",
    "start_time": "00:00:00",
    "end_date": "2020-10-20",
    "end_time": "01:00:00",
    "business_hour": 1,
    "action": "Delete",
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
                datetime.fromisocalendar(YEAR, WEEK, i)
                .date()
                .strftime("(%b. %-d)")
            )
            AssertThat(context["days_of_week"][i - 1]["name"]).IsEqualTo(
                datetime.fromisocalendar(YEAR, WEEK, i).date().strftime("%a")
            )

        AssertThat(r.data).Contains(b'value="<"')
        AssertThat(r.data).Contains(b'value=">"')

    @logged_in_user()
    def test_get_week_post_renders_week_template(self, default_user):
        self.__insert_week()
        r = self.client.post(f"/{YEAR}/{WEEK}", data=TEST_EVENT)

        template, context = self.rendered_templates[0]

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("week.html")
        AssertThat(context["year_number"]).IsEqualTo(YEAR)
        AssertThat(context["week_number"]).IsEqualTo(WEEK)

        for i in range(1, 8):
            AssertThat(context["days_of_week"][i - 1]["date"]).IsEqualTo(
                datetime.fromisocalendar(YEAR, WEEK, i)
                .date()
                .strftime("(%b. %-d)")
            )
            AssertThat(context["days_of_week"][i - 1]["name"]).IsEqualTo(
                datetime.fromisocalendar(YEAR, WEEK, i).date().strftime("%a")
            )

    @logged_in_user()
    def test_get_week_get_persists_week_into_db(self, default_user):
        r = self.client.get(f"/{YEAR}/{WEEK}")

        week = Week.query.filter_by(year=YEAR, week_num=WEEK).first()

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(week.year).IsEqualTo(YEAR)
        AssertThat(week.week_num).IsEqualTo(WEEK)

    @data((2020, 54, 1), (2020, 0, 52), (2019, 53, 1), (2021, 0, 53))
    @unpack
    @logged_in_user()
    def test_get_week_handles_invalid_week(
        self, year, week, expected_week, default_user
    ):
        r = self.client.get(f"/{year}/{week}")

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(r.data).Contains(f"Week - {expected_week}".encode())

    @data((2020, 54, 1), (2020, 0, 52), (2019, 53, 1), (2021, 0, 53))
    @unpack
    @logged_in_user()
    def test_post_week_handles_invalid_week(
        self, year, week, expected_week, default_user
    ):
        r = self.client.post(f"/{year}/{week}", data=TEST_EVENT)

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(r.data).Contains(f"Week - {expected_week}".encode())

    @logged_in_user()
    def test_get_week_get_does_not_save_already_existing_week_again(
        self, default_user
    ):
        self.__insert_week()
        r = self.client.get(f"/{YEAR}/{WEEK}")

        weeks = Week.query.filter_by(year=YEAR, week_num=WEEK).all()

        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(len(weeks)).IsEqualTo(1)

    @logged_in_user()
    def test_get_week_post_saves_event_to_db(self, default_user):
        self.__insert_week()
        r = self.client.post(f"/{YEAR}/{WEEK}", data=TEST_EVENT)

        AssertThat(r.status_code).IsEqualTo(200)
        event = Event.query.filter_by(title=TEST_EVENT["title"]).first()

        AssertThat(event.title).IsEqualTo(TEST_EVENT["title"])
        AssertThat(event.description).IsEqualTo(TEST_EVENT["description"])
        AssertThat(event.location).IsEqualTo(TEST_EVENT["location"])
        AssertThat(event.start).IsEqualTo(
            datetime.strptime(
                f"{TEST_EVENT['start_date']} {TEST_EVENT['start_time']}",
                "%Y-%m-%d %H:%M:%S",
            )
        )
        AssertThat(event.end).IsEqualTo(
            datetime.strptime(
                f"{TEST_EVENT['end_date']} {TEST_EVENT['end_time']}",
                "%Y-%m-%d %H:%M:%S",
            )
        )
        AssertThat(event.event_type).IsEqualTo(TEST_EVENT["business_hour"])

        week = Week.query.filter_by(year=YEAR, week_num=WEEK).first()

        AssertThat(len(week.events)).IsEqualTo(1)
        AssertThat(week.events[0].title).IsEqualTo(TEST_EVENT["title"])

        AssertThat(week.events[0].user_id).IsEqualTo(default_user.id)

    @logged_in_user()
    def test_get_week_post_does_not_save_event_on_delete(self, default_user):
        self.__insert_week()
        r = self.client.post(f"/{YEAR}/{WEEK}", data=TEST_DELETE_EVENT)

        AssertThat(r.status_code).IsEqualTo(200)
        event = Event.query.filter_by(title=TEST_DELETE_EVENT["title"]).first()

        AssertThat(event).IsEqualTo(None)

    @logged_in_user()
    def test_get_week_post_does_not_save_overlapping_event(self, default_user):
        week = self.__insert_week()
        self.__insert_event(default_user.id, week.id)

        overlapping_event = {
            "event-id": -1,
            "title": "test_title",
            "description": "test_description",
            "location": "test_location",
            "start_date": "2020-10-20",
            "start_time": "02:00:00",
            "end_date": "2020-10-20",
            "end_time": "04:00:00",
            "business_hour": 1,
            "action": "Save",
            "guest-name": "",
        }

        r = self.client.post(f"/{YEAR}/{WEEK}", data=overlapping_event)

        template, context = self.rendered_templates[0]

        AssertThat(template.name).IsEqualTo("event.html")
        AssertThat(r.data).Contains(b"Overlapping event!")

    @logged_in_user()
    def test_get_week_post_does_not_save_event_with_end_earlier_than_start(
        self, default_user
    ):
        self.__insert_week()

        wrong_end_event = {
            "event-id": -1,
            "title": "test_title",
            "description": "test_description",
            "location": "test_location",
            "start_date": "2020-10-20",
            "start_time": "02:00:00",
            "end_date": "2020-10-20",
            "end_time": "01:00:00",
            "business_hour": 1,
            "action": "Save",
            "guest-name": "",
        }

        r = self.client.post(f"/{YEAR}/{WEEK}", data=wrong_end_event)

        template, context = self.rendered_templates[0]

        AssertThat(template.name).IsEqualTo("event.html")
        AssertThat(r.data).Contains(
            b"End of event cannot be earlier than (or equal to) its start!"
        )

    @logged_in_user()
    def test_get_week_post_does_not_save_events_with_equal_end_and_start(
        self, default_user
    ):
        self.__insert_week()

        wrong_end_event = {
            "event-id": -1,
            "title": "test_title",
            "description": "test_description",
            "location": "test_location",
            "start_date": "2020-10-20",
            "start_time": "02:00:00",
            "end_date": "2020-10-20",
            "end_time": "02:00:00",
            "business_hour": 1,
            "action": "Save",
            "guest-name": "",
        }

        r = self.client.post(f"/{YEAR}/{WEEK}", data=wrong_end_event)

        template, context = self.rendered_templates[0]

        AssertThat(template.name).IsEqualTo("event.html")
        AssertThat(r.data).Contains(
            b"End of event cannot be earlier than (or equal to) its start!"
        )

    @logged_in_user()
    def test_get_week_post_does_not_save_event_ending_on_the_next_day(
        self, default_user
    ):
        self.__insert_week()

        wrong_end_event = {
            "event-id": -1,
            "title": "test_title",
            "description": "test_description",
            "location": "test_location",
            "start_date": "2020-10-20",
            "start_time": "02:00:00",
            "end_date": "2020-10-21",
            "end_time": "01:00:00",
            "business_hour": 1,
            "action": "Save",
            "guest-name": "",
        }

        r = self.client.post(f"/{YEAR}/{WEEK}", data=wrong_end_event)

        template, context = self.rendered_templates[0]

        AssertThat(template.name).IsEqualTo("event.html")
        AssertThat(r.data).Contains(b"Event ends on a different day!")

    @logged_in_user()
    def test_get_week_event_insertion_handles_wrongly_formatted_time(
        self, default_user
    ):
        self.__insert_week()

        wrong_time_event = {
            "event-id": -1,
            "title": "test_title",
            "description": "test_description",
            "location": "test_location",
            "start_date": "2020-10-20",
            "start_time": "02:00",
            "end_date": "2020-10-20",
            "end_time": "03:00",
            "business_hour": 1,
            "action": "Save",
            "guest-name": "",
        }

        r = self.client.post(f"/{YEAR}/{WEEK}", data=wrong_time_event)

        template, context = self.rendered_templates[0]

        AssertThat(template.name).IsEqualTo("week.html")
        AssertThat(r.data).Contains(wrong_time_event["title"].encode())

    @logged_in_user()
    def test_get_week_post_shows_saved_events(self, default_user):
        self.__insert_week()
        r = self.client.post(f"/{YEAR}/{WEEK}", data=TEST_EVENT)

        template, context = self.rendered_templates[0]

        AssertThat(r.data).Contains(TEST_EVENT["title"].encode())

    @logged_in_user()
    def test_get_week_event_creation_is_enabled(self, default_user):
        self.__insert_week()
        r = self.client.post(f"/{YEAR}/{WEEK}", data=TEST_EVENT)

        template, context = self.rendered_templates[0]

        AssertThat(r.data).Contains(b"btn-4-5")

    @logged_in_user()
    def test_get_week_event_is_enabled(self, default_user):
        week = self.__insert_week()
        event = self.__insert_event(default_user.id, week.id)
        new_title = "another_title"
        modified_event = {
            "event-id": event.id,
            "title": new_title,
            "description": event.description,
            "location": event.location,
            "start_date": event.start.date(),
            "start_time": event.start.time(),
            "end_date": event.end.date(),
            "end_time": event.end.time(),
            "business_hour": event.event_type,
            "action": "Save",
            "guest-name": "",
        }
        r = self.client.post(f"/{YEAR}/{WEEK}", data=modified_event)

        AssertThat(r.data).Contains(new_title.encode())

    @logged_in_user()
    def test_get_week_event_modification_handles_wrongly_formatted_time(
        self, default_user
    ):
        week = self.__insert_week()
        event = self.__insert_event(default_user.id, week.id)
        modified_event = {
            "event-id": event.id,
            "title": event.title,
            "description": event.description,
            "location": event.location,
            "start_date": event.start.date(),
            "start_time": "02:00",
            "end_date": event.end.date(),
            "end_time": "03:00",
            "business_hour": event.event_type,
            "action": "Save",
            "guest-name": "",
        }
        r = self.client.post(f"/{YEAR}/{WEEK}", data=modified_event)

        template, context = self.rendered_templates[0]

        AssertThat(template.name).IsEqualTo("week.html")
        AssertThat(r.data).Contains(modified_event["title"].encode())

    @logged_in_user()
    def test_shared_calendar_shows_created_events(self, default_user):
        self.__insert_week()
        r = self.client.post(f"/{YEAR}/{WEEK}", data=TEST_EVENT)

        template, context = self.rendered_templates[0]

        token = UserAccess(
            current_app.config["SHARING_TOKEN_SECRET"]
        ).generate(default_user.id, timedelta(days=1))

        r = self.client.get(f"/{YEAR}/{WEEK}/shared-calendar/{token}")

        AssertThat(r.data).Contains(TEST_EVENT["title"].encode())

    @logged_in_user()
    def test_shared_calendar_share_content_enables_viewing_events(
        self, default_user
    ):
        week = self.__insert_week()
        self.__insert_event(default_user.id, week.id)

        token = UserAccess(
            current_app.config["SHARING_TOKEN_SECRET"]
        ).generate(default_user.id, timedelta(days=1), True)

        r = self.client.get(f"/{YEAR}/{WEEK}/shared-calendar/{token}")

        AssertThat(r.data).DoesNotContain(b"disabled")

    @logged_in_user()
    def test_shared_calendar_not_sharing_content_disables_viewing_events(
        self, default_user
    ):
        week = self.__insert_week()
        self.__insert_event(default_user.id, week.id)

        token = UserAccess(
            current_app.config["SHARING_TOKEN_SECRET"]
        ).generate(default_user.id, timedelta(days=1), False)

        r = self.client.get(f"/{YEAR}/{WEEK}/shared-calendar/{token}")

        AssertThat(r.data).Contains(b"disabled")

    def __insert_event(
        self,
        user_id,
        week_id,
        event_type=1,
        title="test_title",
        description="test_description",
        location="test_location",
        start_date="2020-10-20",
        start_time="02:00:00",
        end_date="2020-10-20",
        end_time="03:00:00",
        guest_name="",
    ):
        event = Event(
            event_type=event_type,
            title=title,
            description=description,
            location=location,
            start=f"{start_date} {start_time}",
            end=f"{end_date} {end_time}",
            guest_name=guest_name,
            week_id=week_id,
            user_id=user_id,
        )
        db.session.add(event)
        db.session.commit()

        return event

    def __insert_week(self, year=YEAR, week_number=WEEK):
        week = Week(year=year, week_num=week_number)
        db.session.add(week)
        db.session.commit()

        return week
