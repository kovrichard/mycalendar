import unittest

from truth.truth import AssertThat

from mycalendar.db_models.role import Role
from tests import AppTestCase, DbMixin

from mycalendar.db_models import db

class RoleTest(DbMixin, AppTestCase):
    def setUp(self):
        super().setUp()
        Role.query.delete()

    def test_role_can_be_inserted_and_queried(self):
        db.session.add(Role(name="admin"))

        AssertThat(Role.query.filter_by(name="admin").first().name).IsEqualTo(
            "admin"
        )
