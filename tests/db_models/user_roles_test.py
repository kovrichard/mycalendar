from truth.truth import AssertThat

from mycalendar.db_models import db
from mycalendar.db_models.db_event import Event
from mycalendar.db_models.db_role import Role
from mycalendar.db_models.db_user import User
from mycalendar.db_models.db_user_roles import UserRoles
from tests import AppTestCase, DbMixin


class UserRolesTest(DbMixin, AppTestCase):
    def setUp(self):
        super().setUp()
        Event.query.delete()
        UserRoles.query.delete()
        User.query.delete()
        Role.query.delete()

    def test_role_can_be_assigned_to_user(self):
        db.session.add(User(username="<username>", password="<password>"))
        db.session.add(Role(name="<role>"))
        user = User.query.filter_by(username="<username>").first()
        role = Role.query.filter_by(name="<role>").first()
        db.session.add(UserRoles(user_id=user.id, role_id=role.id))

        AssertThat(
            UserRoles.query.filter_by(user_id=user.id).first().role_id
        ).IsEqualTo(role.id)
