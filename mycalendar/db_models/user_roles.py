from . import db


class UserRoles(db.Model):
    __tablename__ = "user_roles"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE"))
    role_id = db.Column(db.Integer(), db.ForeignKey("roles.id", ondelete="CASCADE"))

    def __repr__(self):
        return "<UserRole(id='%d', user_id='%d', role_id='%d')>" % (
            self.id,
            self.user_id,
            self.role_id,
        )
