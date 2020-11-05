from datetime import datetime, timedelta

import jwt


class UserAccess:
    def __init__(self, secret):
        self.secret = secret

    def generate(self, user_id, validity_period: timedelta, share_all=False):
        return jwt.encode(
            {
                "user_id": user_id,
                "share_all": share_all,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + validity_period,
            },
            self.secret,
            algorithm="HS256",
        ).decode()

    def decode(self, token):
        try:
            decoded_token = jwt.decode(
                token,
                self.secret,
                algorithm="HS256",
                options={"require_iat": True, "require_exp": True},
            )
        except jwt.DecodeError:
            return None
        except jwt.ExpiredSignatureError:
            return None

        return decoded_token
