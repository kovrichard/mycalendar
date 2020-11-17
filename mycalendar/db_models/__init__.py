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
    from .db_event import Event
    from .db_role import Role
    from .db_user import User
    from .db_user_roles import UserRoles
    from .db_week import Week


def init_db(app):
    import_models()

    db.init_app(app)
