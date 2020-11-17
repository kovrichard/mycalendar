from truth.truth import AssertThat

from mycalendar.db_models import db
from mycalendar.db_models.db_event import Event
from mycalendar.db_models.db_week import Week
from tests import AppTestCase, DbMixin


class WeekTest(DbMixin, AppTestCase):
    def setUp(self):
        super().setUp()
        Event.query.delete()
        Week.query.delete()

    def test_week_and_event_can_be_inserted_and_queried(self):
        event = Event(
            event_type=0,
            title="<event>",
            description="<description>",
            location="<location>",
            start="2020-10-19 00:00:00",
            end="2020-10-19 01:00:00",
        )
        db.session.add(event)
        db.session.add(Week(year=2020, week_num=1, events=[event]))
        db.session.commit()

        AssertThat(
            len(Week.query.filter_by(week_num=1).first().events)
        ).IsEqualTo(1)

        queried_week_event = Week.query.filter_by(week_num=1).first().events[0]

        AssertThat(queried_week_event.event_type).IsEqualTo(event.event_type)
        AssertThat(queried_week_event.title).IsEqualTo(event.title)
        AssertThat(queried_week_event.description).IsEqualTo(event.description)
        AssertThat(queried_week_event.location).IsEqualTo(event.location)
        AssertThat(queried_week_event.start).IsEqualTo(event.start)
        AssertThat(queried_week_event.end).IsEqualTo(event.end)
        AssertThat(queried_week_event.guest_name).IsEqualTo(event.guest_name)
