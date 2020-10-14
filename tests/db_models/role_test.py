import unittest

from truth.truth import AssertThat

from mycalendar.db_models import session
from mycalendar.db_models.role import Role


class RoleTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        session.query(Role).delete()

    def test_role_can_be_inserted_and_queried(self):
        session.add(Role(name="admin"))

        AssertThat(session.query(Role).filter_by(name="admin").first().name).IsEqualTo(
            "admin"
        )
