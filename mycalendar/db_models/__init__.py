from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def import_models():
    from .user import User


def init_db(app):
    import_models()

    db.init_app(app)
