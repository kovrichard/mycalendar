from sqlalchemy import Column, ForeignKey, Integer

from . import Base


class UserRoles(Base):
    __tablename__ = "user_roles"

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey("users.id", ondelete="CASCADE"))
    role_id = Column(Integer(), ForeignKey("roles.id", ondelete="CASCADE"))

    def __repr__(self):
        return "<UserRole(id='%d', user_id='%d', role_id='%d')>" % (
            self.id,
            self.user_id,
            self.role_id,
        )
