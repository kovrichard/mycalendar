from truth.truth import AssertThat

from mycalendar.db_models import db
from mycalendar.db_models.user import User
from tests import AppTestCase, DbMixin


class UserTest(DbMixin, AppTestCase):
    def setUp(self):
        super().setUp()
        User.query.delete()

    def test_get_or_query_works(self):
        user = User.query.get_or(10, 1)

        AssertThat(user).IsEqualTo(1)

    def test_user_can_be_inserted_and_queried(self):
        db.session.add(User(username="<user>", password="<password>"))

        AssertThat(
            User.query.filter_by(username="<user>").first().password
        ).IsEqualTo("<password>")
