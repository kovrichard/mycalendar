# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import Query, sessionmaker

# from mycalendar.server.config import DB_URL

# Base = declarative_base()

from flask_sqlalchemy import SQLAlchemy, BaseQuery

class GetOrQuery(BaseQuery):
    def get_or(self, ident, default=None):
        return self.get(ident) or default

db = SQLAlchemy(query_class=GetOrQuery)


# engine = create_engine(DB_URL)
# Session = sessionmaker()
# Session.configure(bind=engine, query_cls=GetOrQuery)
# session = Session()


def import_models():
    from .role import Role
    from .user import User
    from .user_roles import UserRoles


def init_db(app):
    import_models()

    db.init_app(app)
