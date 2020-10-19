from truth.truth import AssertThat

from mycalendar.db_models import db
from mycalendar.db_models.event import Event
from mycalendar.db_models.week import Week
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
        db.session.add(Week(week_num=1, events=[event]))
        db.session.commit()

        AssertThat(
            len(Week.query.filter_by(week_num=1).first().events)
        ).IsEqualTo(1)
        AssertThat(
            Week.query.filter_by(week_num=1).first().events[0].event_type
        ).IsEqualTo(event.event_type)
        AssertThat(
            Week.query.filter_by(week_num=1).first().events[0].title
        ).IsEqualTo(event.title)
        AssertThat(
            Week.query.filter_by(week_num=1).first().events[0].description
        ).IsEqualTo(event.description)
        AssertThat(
            Week.query.filter_by(week_num=1).first().events[0].location
        ).IsEqualTo(event.location)
        AssertThat(
            Week.query.filter_by(week_num=1).first().events[0].start
        ).IsEqualTo(event.start)
        AssertThat(
            Week.query.filter_by(week_num=1).first().events[0].end
        ).IsEqualTo(event.end)
