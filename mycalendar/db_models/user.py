# from . import db
from sqlalchemy import Column, Integer, String

from . import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))

    def __repr__(self):
        return "<User(id=%d', username='%s', password='%s')>" % (
            self.id,
            self.username,
            self.password,
        )
