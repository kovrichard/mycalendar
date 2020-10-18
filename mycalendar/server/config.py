import os

DB_URL = os.environ.get("DB_URL")

SECRET_KEY = os.environ.get("SECRET_KEY")
USER_ENABLE_EMAIL = False
USER_AFTER_LOGIN_ENDPOINT = "main.get_main"
