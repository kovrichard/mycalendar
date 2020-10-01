from flask_sqlalchemy import BaseQuery, SQLAlchemy


class GetOrQuery(BaseQuery):
    def get_or(self, ident, default=None):
        return self.get(ident) or default


db = SQLAlchemy(query_class=GetOrQuery)


def import_models():
    from .user import User


def init_db(app):
    import_models()

    db.init_app(app)
