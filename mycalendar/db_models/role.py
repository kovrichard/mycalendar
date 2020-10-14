from sqlalchemy import Column, Integer, String

from . import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer(), primary_key=True)
    name = Column(String(50), unique=True)

    def __repr__(self):
        return "<Role(id='%d', name='%s')>" % (self.id, self.name)
