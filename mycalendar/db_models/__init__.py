# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import Query, sessionmaker

# from mycalendar.server.config import DATABASE_URL

# Base = declarative_base()

from flask_sqlalchemy import BaseQuery, SQLAlchemy


class GetOrQuery(BaseQuery):
    def get_or(self, ident, default=None):
        return self.get(ident) or default


db = SQLAlchemy(query_class=GetOrQuery)


# engine = create_engine(DATABASE_URL)
# Session = sessionmaker()
# Session.configure(bind=engine, query_cls=GetOrQuery)
# session = Session()


def import_models():
    from .event import Event
    from .role import Role
    from .user import User
    from .user_roles import UserRoles
    from .week import Week


def init_db(app):
    import_models()

    db.init_app(app)
