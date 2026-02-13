"""
Supabase Data Manager - Đồng bộ dữ liệu giữa Supabase và SQLite
"""

import os
from typing import Optional, Callable
from dotenv import load_dotenv
import httpx

from database import TABLE_SCHEMAS

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# Page size cho paginated fetch
PAGE_SIZE = 1000


class SupabaseDataManager:
    """Quản lý đồng bộ dữ liệu giữa Supabase và SQLite."""

    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            raise ValueError("Thiếu SUPABASE_URL hoặc SUPABASE_ANON_KEY trong .env")

    def _get_headers(self, use_service_role: bool = False) -> dict:
        """Tạo headers cho Supabase REST API."""
        key = SUPABASE_SERVICE_ROLE_KEY if use_service_role else SUPABASE_ANON_KEY
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

    def fetch_table_data(self, table_name: str,
                         progress_callback: Optional[Callable] = None) -> list:
        """
        Lấy toàn bộ dữ liệu từ bảng Supabase (paginated).
        Returns: list of tuples (mỗi tuple = 1 row dữ liệu).
        """
        columns = TABLE_SCHEMAS.get(table_name)
        if not columns:
            raise ValueError(f"Bảng '{table_name}' không tồn tại trong schema")

        col_names = [col_name for col_name, _ in columns]
        select = ",".join(col_names)

        all_rows = []
        offset = 0
        headers = self._get_headers()

        while True:
            url = (
                f"{SUPABASE_URL}/rest/v1/{table_name}"
                f"?select={select}&offset={offset}&limit={PAGE_SIZE}"
                f"&order=id.asc"
            )
            try:
                response = httpx.get(url, headers=headers, timeout=30.0)
                if response.status_code != 200:
                    raise Exception(
                        f"Lỗi API: {response.status_code} - {response.text}"
                    )

                data = response.json()
                if not data:
                    break

                for row_dict in data:
                    row_tuple = tuple(
                        str(row_dict.get(col, "") or "") for col in col_names
                    )
                    all_rows.append(row_tuple)

                if progress_callback:
                    progress_callback(len(all_rows))

                if len(data) < PAGE_SIZE:
                    break

                offset += PAGE_SIZE
            except httpx.TimeoutException:
                raise Exception("Hết thời gian kết nối. Vui lòng thử lại.")
            except httpx.ConnectError:
                raise Exception("Không thể kết nối đến server. Kiểm tra kết nối internet.")

        return all_rows

    def push_table_data(self, table_name: str, rows: list,
                        progress_callback: Optional[Callable] = None) -> int:
        """
        Đẩy dữ liệu từ SQLite lên Supabase (admin only).
        Xóa dữ liệu cũ trên Supabase rồi insert mới.
        Returns: số dòng đã push.
        """
        if not SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("Thiếu SUPABASE_SERVICE_ROLE_KEY. Chỉ admin mới có quyền!")

        columns = TABLE_SCHEMAS.get(table_name)
        if not columns:
            raise ValueError(f"Bảng '{table_name}' không tồn tại")

        col_names = [col_name for col_name, _ in columns]
        headers = self._get_headers(use_service_role=True)

        # 1. Xóa dữ liệu cũ trên Supabase
        delete_url = f"{SUPABASE_URL}/rest/v1/{table_name}?id=gt.0"
        response = httpx.delete(delete_url, headers=headers, timeout=30.0)
        if response.status_code not in (200, 204):
            raise Exception(f"Không thể xóa dữ liệu cũ: {response.status_code}")

        # 2. Insert dữ liệu mới theo batch
        total_pushed = 0
        batch_size = 500

        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            json_batch = []
            for row in batch:
                row_dict = {}
                for j, col_name in enumerate(col_names):
                    row_dict[col_name] = str(row[j]) if j < len(row) and row[j] else ""
                json_batch.append(row_dict)

            insert_url = f"{SUPABASE_URL}/rest/v1/{table_name}"
            response = httpx.post(
                insert_url, headers=headers, json=json_batch, timeout=60.0
            )
            if response.status_code not in (200, 201):
                raise Exception(
                    f"Lỗi insert batch {i}: {response.status_code} - {response.text}"
                )

            total_pushed += len(batch)
            if progress_callback:
                progress_callback(total_pushed, len(rows))

        return total_pushed

    def get_table_count(self, table_name: str) -> int:
        """Lấy số lượng dòng trong bảng Supabase."""
        headers = self._get_headers()
        headers["Prefer"] = "count=exact"
        headers["Range-Unit"] = "items"
        headers["Range"] = "0-0"

        url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=id"
        try:
            response = httpx.get(url, headers=headers, timeout=10.0)
            content_range = response.headers.get("content-range", "")
            if "/" in content_range:
                total = content_range.split("/")[1]
                return int(total) if total != "*" else 0
            return 0
        except Exception:
            return 0
