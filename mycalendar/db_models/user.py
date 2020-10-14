from flask_user import UserMixin
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    roles = relationship("Role", secondary="user_roles")

    def __repr__(self):
        return "<User(id=%d', username='%s', password='%s')>" % (
            self.id,
            self.username,
            self.password,
        )
