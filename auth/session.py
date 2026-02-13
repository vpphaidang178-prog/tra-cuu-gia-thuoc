"""
Session - Quản lý phiên đăng nhập
"""


class Session:
    """Lưu thông tin phiên đăng nhập."""

    def __init__(self, user_data: dict = None):
        if user_data:
            self.user_id = user_data.get("user_id", "")
            self.username = user_data.get("username", "")
            self.role = user_data.get("role", "user")
            self.access_token = user_data.get("access_token", "")
        else:
            self.user_id = ""
            self.username = ""
            self.role = "user"
            self.access_token = ""

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_authenticated(self) -> bool:
        return bool(self.user_id)
