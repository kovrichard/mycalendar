from mycalendar.db_models import session
from mycalendar.db_models.user import User

import unittest

from truth.truth import AssertThat

class UserTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        session.query(User).delete()

    def test_user_can_be_inserted_and_queried(self):
        session.add(User(username="<user>", password="<password>"))

        AssertThat(session.query(User).filter_by(username="<user>").first().password).IsEqualTo("<password>")