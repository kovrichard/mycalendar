import random
import unittest
from contextlib import contextmanager
from functools import wraps

from flask import template_rendered

from mycalendar.server.factory import create_app


class AppTestCase(unittest.TestCase):
    def __init__(self, methodName):
        self.app = create_app()
        super().__init__(methodName)


class DbMixin:
    def run(self, result=None):
        with self.app.app_context() as ctx:
            self.app_ctx = ctx
            super().run(result)

    def add_user(self, role="admin"):
        db_manager = self.app.user_manager.db_manager
        username = str(random.randrange(100001, 999999, 2))
        password = username[::-1]

        user = db_manager.add_user(
            username=username,
            password=self.app.user_manager.hash_password(password),
        )
        db_manager.add_user_role(user, role)

        return user


class TestClientMixin:
    def run(self, result=None):
        with self.app.test_client() as client:
            self.client = client
            super().run(result)

    def login(self, user):
        with self.client.session_transaction() as session:
            session["_user_id"] = user.get_id()

    def logout(self):
        with self.client.session_transaction() as session:
            session["_user_id"] = None

    @contextmanager
    def logged_in_user(self, role="admin"):
        user = self.add_user(role)
        self.login(user)
        yield user
        self.logout()


class TemplateRenderMixin:
    def run(self, result=None):
        self.rendered_templates = []

        def record(sender, template, context, **extra):
            self.rendered_templates.append((template, context))

        template_rendered.connect(record, self.app)
        super().run(result)
        template_rendered.disconnect(record, self.app)


def logged_in_user(role="admin"):
    def wrap(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # self.logged_in_user()
            with args[0].logged_in_user(role) as user:
                args = list(args)
                args.append(user)
                return f(*args, **kwargs)

        return wrapper

    return wrap
