from datetime import datetime, timedelta


class ShareController:
    def get_default_expiration(self):
        return datetime.now().date() + timedelta(days=7)
