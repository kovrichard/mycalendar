import os

DATABASE_URL = os.environ.get("DATABASE_URL")

SECRET_KEY = os.environ.get("SECRET_KEY")

USER_ENABLE_EMAIL = False
USER_ENABLE_CHANGE_USERNAME = False
USER_ENABLE_CHANGE_PASSWORD = False

USER_AFTER_LOGIN_ENDPOINT = "main.main"
USER_AFTER_LOGOUT_ENDPOINT = "user.login"
USER_AFTER_EDIT_USER_PROFILE_ENDPOINT = "user.edit_user_profile"

CALENDAR_URL = os.environ.get("CALENDAR_URL")
SHARING_TOKEN_SECRET = os.environ.get("SHARING_TOKEN_SECRET")
