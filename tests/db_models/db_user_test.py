from truth.truth import AssertThat

from mycalendar.db_models import db
from mycalendar.db_models.db_event import Event
from mycalendar.db_models.db_user import User
from tests import AppTestCase, DbMixin


class UserTest(DbMixin, AppTestCase):
    def setUp(self):
        super().setUp()
        Event.query.delete()
        User.query.delete()

    def test_get_or_query_works(self):
        user = User.query.get_or(10, 1)

        AssertThat(user).IsEqualTo(1)

    def test_user_can_be_inserted_and_queried(self):
        user = User(username="<username>", password="<password>")
        db.session.add(user)

        AssertThat(
            User.query.filter_by(username=user.username).first().password
        ).IsEqualTo(user.password)
