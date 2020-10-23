import unittest
from datetime import timedelta

from truth.truth import AssertThat

from mycalendar.lib.user_access import UserAccess

USER_ID = 3


class UserAccessTest(unittest.TestCase):
    def setUp(self):
        self.user_access = UserAccess("SECRET")
        self.validity_period = timedelta(days=1)
        self.token = self.user_access.generate(USER_ID, self.validity_period)

    def test_generate_generates_user_access_token(self):
        AssertThat(self.token).IsNotNone()

    def test_decode_decodes_user_access_token(self):
        user_id = self.user_access.decode(self.token)
        AssertThat(user_id).IsEqualTo(USER_ID)

    def test_decode_denies_access_for_invalid_secret(self):
        token = UserAccess("DIFFERENT_SECRET").generate(
            USER_ID, self.validity_period
        )

        AssertThat(self.user_access.decode(token)).IsNone()

    def test_decode_expiration_date_is_taken_into_account(self):
        token = self.user_access.generate(USER_ID, timedelta(days=-1))

        AssertThat(self.user_access.decode(token)).IsNone()

    def test_generate_raises_error_if_no_expiration_is_set(self):
        with self.assertRaises(TypeError):
            self.user_access.generate(USER_ID)
