"""
Supabase Auth Client - Xác thực bằng username/password
Lưu tài khoản trong bảng app_users trên Supabase (không cần email)
"""

import os
import hashlib
import secrets
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


def _hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash password với salt. Trả về (hash, salt)."""
    if salt is None:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return pw_hash, salt


def _verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Kiểm tra password có khớp không."""
    pw_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return pw_hash == stored_hash


class SupabaseAuth:
    """Xác thực người dùng bằng username/password qua bảng app_users."""

    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.service_key = SUPABASE_SERVICE_ROLE_KEY
        self.anon_key = SUPABASE_ANON_KEY

    def _headers(self, use_service_role: bool = False) -> dict:
        key = self.service_key if use_service_role else self.anon_key
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

    def login(self, username: str, password: str) -> tuple[bool, str, dict]:
        """
        Đăng nhập bằng username/password.
        Returns: (success, message, user_data)
        """
        try:
            # Tìm user theo username
            url = (
                f"{self.supabase_url}/rest/v1/app_users"
                f"?username=eq.{username}&select=*"
            )
            resp = httpx.get(url, headers=self._headers(True), timeout=15)

            if resp.status_code != 200:
                return False, "Lỗi kết nối server!", {}

            users = resp.json()
            if not users:
                return False, "Tài khoản không tồn tại!", {}

            user = users[0]

            # Verify password
            if not _verify_password(password, user["password_hash"], user["salt"]):
                return False, "Sai mật khẩu!", {}

            user_data = {
                "user_id": str(user["id"]),
                "username": user["username"],
                "role": user["role"],
                "access_token": self.service_key,  # dùng service key cho API
            }

            return True, "Đăng nhập thành công!", user_data

        except httpx.TimeoutException:
            return False, "Hết thời gian kết nối. Kiểm tra internet!", {}
        except Exception as e:
            return False, f"Lỗi: {str(e)}", {}

    def create_user(
        self, username: str, password: str, display_name: str, role: str
    ) -> tuple[bool, str]:
        """
        Tạo tài khoản mới (Admin only).
        Returns: (success, message)
        """
        try:
            # Kiểm tra username đã tồn tại chưa
            check_url = (
                f"{self.supabase_url}/rest/v1/app_users"
                f"?username=eq.{username}&select=id"
            )
            resp = httpx.get(check_url, headers=self._headers(True), timeout=10)
            if resp.status_code == 200 and resp.json():
                return False, f"Tài khoản '{username}' đã tồn tại!"

            # Hash password
            pw_hash, salt = _hash_password(password)

            # Insert user
            url = f"{self.supabase_url}/rest/v1/app_users"
            headers = {**self._headers(True), "Prefer": "return=representation"}
            payload = {
                "username": username,
                "display_name": display_name,
                "password_hash": pw_hash,
                "salt": salt,
                "role": role,
            }

            resp = httpx.post(url, headers=headers, json=payload, timeout=10)

            if resp.status_code in (200, 201):
                return True, f"Tạo tài khoản '{username}' thành công!"
            else:
                return False, f"Lỗi tạo tài khoản: {resp.text}"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def change_password(
        self, username: str, new_password: str
    ) -> tuple[bool, str]:
        """Đổi mật khẩu (Admin only)."""
        try:
            pw_hash, salt = _hash_password(new_password)
            url = (
                f"{self.supabase_url}/rest/v1/app_users"
                f"?username=eq.{username}"
            )
            headers = {**self._headers(True), "Prefer": "return=minimal"}
            payload = {"password_hash": pw_hash, "salt": salt}

            resp = httpx.patch(url, headers=headers, json=payload, timeout=10)

            if resp.status_code in (200, 204):
                return True, f"Đã đổi mật khẩu cho '{username}'!"
            else:
                return False, f"Lỗi: {resp.text}"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def delete_user(self, username: str) -> tuple[bool, str]:
        """Xóa tài khoản (Admin only)."""
        try:
            url = (
                f"{self.supabase_url}/rest/v1/app_users"
                f"?username=eq.{username}"
            )
            headers = {**self._headers(True), "Prefer": "return=minimal"}

            resp = httpx.delete(url, headers=headers, timeout=10)

            if resp.status_code in (200, 204):
                return True, f"Xoa tai khoan '{username}'!"
            else:
                return False, f"Loi: {resp.text}"
        except Exception as e:
            return False, f"Loi: {str(e)}"

    def get_all_users(self) -> list[dict]:
        """Lấy danh sách tất cả tài khoản."""
        try:
            url = (
                f"{self.supabase_url}/rest/v1/app_users"
                f"?select=id,username,display_name,role,created_at"
                f"&order=created_at.asc"
            )
            resp = httpx.get(url, headers=self._headers(True), timeout=10)
            if resp.status_code == 200:
                return resp.json()
            return []
        except Exception:
            return []
