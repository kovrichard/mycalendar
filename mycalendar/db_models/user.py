from flask_user import UserMixin

from . import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(
        "is_active", db.Boolean(), nullable=False, server_default="1"
    )
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default="")
    roles = db.relationship("Role", secondary="user_roles")
    events = db.relationship("Event", backref="User")

    def __repr__(self):
        return "<User(id=%d', active='%s', username='%s', password='%s', roles='%s', events='%s')>" % (
            self.id,
            self.active,
            self.username,
            self.password,
            self.roles,
            self.events,
        )
