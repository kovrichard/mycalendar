import unittest

from truth.truth import AssertThat

from mycalendar.db_models import session
from mycalendar.db_models.role import Role
from mycalendar.db_models.user import User
from mycalendar.db_models.user_roles import UserRoles


class UserRolesTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        session.query(UserRoles).delete()
        session.query(User).delete()
        session.query(Role).delete()

    def test_role_can_be_assigned_to_user(self):
        session.add(User(username="<username>"))
        session.add(Role(name="<role>"))
        user = session.query(User).filter_by(username="<username>").first()
        role = session.query(Role).filter_by(name="<role>").first()
        session.add(UserRoles(user_id=user.id, role_id=role.id))

        AssertThat(
            session.query(UserRoles).filter_by(user_id=user.id).first().role_id
        ).IsEqualTo(role.id)
