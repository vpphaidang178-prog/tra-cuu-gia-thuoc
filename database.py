"""
Database Manager cho ứng dụng Tra Cứu Giá Thuốc
Sử dụng SQLite để lưu trữ dữ liệu thuốc
"""

import sqlite3
import os
import pandas as pd
from typing import Optional


# ============================================================
# SCHEMA: Thuốc Generic / Biệt dược gốc / Thuốc Dược liệu
# ============================================================
THUOC_CHUNG_COLUMNS = [
    ("stt", "TEXT"),
    ("ten_thuoc", "TEXT"),
    ("ten_hoat_chat", "TEXT"),
    ("nong_do_ham_luong", "TEXT"),
    ("gdklh", "TEXT"),
    ("duong_dung", "TEXT"),
    ("dang_bao_che", "TEXT"),
    ("han_dung", "TEXT"),
    ("ten_co_so_san_xuat", "TEXT"),
    ("nuoc_san_xuat", "TEXT"),
    ("quy_cach_dong_goi", "TEXT"),
    ("don_vi_tinh", "TEXT"),
    ("so_luong", "TEXT"),
    ("don_gia", "TEXT"),
    ("nhom_thuoc", "TEXT"),
    ("ma_tbmt", "TEXT"),
    ("ten_cdt", "TEXT"),
    ("hinh_thuc_lcnt", "TEXT"),
    ("ngay_dang_tai", "TEXT"),
    ("so_quyet_dinh", "TEXT"),
    ("ngay_ban_hanh", "TEXT"),
    ("so_nha_thau", "TEXT"),
    ("dia_diem", "TEXT"),
]

THUOC_CHUNG_HEADERS = [
    "STT", "Tên thuốc", "Tên hoạt chất/thành phần dược liệu",
    "Nồng độ, hàm lượng", "GĐKLH", "Đường dùng", "Dạng bào chế",
    "Hạn dùng (Tuổi thọ)", "Tên cơ sở sản xuất", "Nước sản xuất",
    "Quy cách đóng gói", "Đơn vị tính", "Số lượng", "Đơn giá (VND)",
    "Nhóm thuốc", "Mã TBMT", "Tên CĐT", "Hình thức LCNT",
    "Ngày đăng tải KQLCNT", "Số quyết định", "Ngày ban hành quyết định",
    "Số nhà thầu tham dự", "Địa điểm"
]

# Thuốc Generic
THUOC_GENERIC_COLUMNS = THUOC_CHUNG_COLUMNS[:]
THUOC_GENERIC_HEADERS = THUOC_CHUNG_HEADERS[:]

# Biệt dược gốc
THUOC_BIET_DUOC_COLUMNS = THUOC_CHUNG_COLUMNS[:]
THUOC_BIET_DUOC_HEADERS = THUOC_CHUNG_HEADERS[:]

# Thuốc Dược liệu
THUOC_DUOC_LIEU_COLUMNS = THUOC_CHUNG_COLUMNS[:]
THUOC_DUOC_LIEU_HEADERS = THUOC_CHUNG_HEADERS[:]

# ============================================================
# SCHEMA: Dược liệu (raw)
# ============================================================
DUOC_LIEU_COLUMNS = [
    ("stt", "TEXT"),
    ("ten_duoc_lieu", "TEXT"),
    ("bo_phan_dung", "TEXT"),
    ("ten_khoa_hoc", "TEXT"),
    ("nguon_goc", "TEXT"),
    ("phuong_phap_che_bien", "TEXT"),
    ("so_dklh_giay_phep", "TEXT"),
    ("ten_co_so_san_xuat", "TEXT"),
    ("nuoc_san_xuat", "TEXT"),
    ("quy_cach_dong_goi", "TEXT"),
    ("don_vi_tinh", "TEXT"),
    ("so_luong", "TEXT"),
    ("don_gia_trung_thau", "TEXT"),
    ("nhom_tckt", "TEXT"),
    ("ma_tbmt", "TEXT"),
    ("ten_cdt", "TEXT"),
    ("hinh_thuc_lcnt", "TEXT"),
    ("ngay_dang_tai", "TEXT"),
    ("so_quyet_dinh", "TEXT"),
    ("ngay_ban_hanh", "TEXT"),
    ("so_nha_thau", "TEXT"),
    ("dia_diem", "TEXT"),
]

DUOC_LIEU_HEADERS = [
    "STT", "Tên dược liệu", "Bộ phận dùng", "Tên khoa học",
    "Nguồn gốc", "Phương pháp chế biến", "Số ĐKLH/Giấy phép NK",
    "Tên cơ sở sản xuất", "Nước sản xuất", "Quy cách đóng gói",
    "Đơn vị tính", "Số lượng", "Đơn giá trúng thầu", "Nhóm TCKT",
    "Mã TBMT", "Tên CĐT", "Hình thức LCNT", "Ngày đăng tải KQLCNT",
    "Số quyết định", "Ngày ban hành quyết định", "Số nhà thầu tham dự",
    "Địa điểm"
]

# ============================================================
# SCHEMA: Vị thuốc cổ truyền
# ============================================================
VI_THUOC_COLUMNS = [
    ("stt", "TEXT"),
    ("ten_vi_thuoc", "TEXT"),
    ("bo_phan_dung", "TEXT"),
    ("ten_khoa_hoc", "TEXT"),
    ("nguon_goc", "TEXT"),
    ("phuong_phap_che_bien", "TEXT"),
    ("so_dklh_giay_phep", "TEXT"),
    ("ten_co_so_san_xuat", "TEXT"),
    ("nuoc_san_xuat", "TEXT"),
    ("quy_cach_dong_goi", "TEXT"),
    ("don_vi_tinh", "TEXT"),
    ("so_luong", "TEXT"),
    ("don_gia_trung_thau", "TEXT"),
    ("nhom_tckt", "TEXT"),
    ("ma_tbmt", "TEXT"),
    ("ten_cdt", "TEXT"),
    ("hinh_thuc_lcnt", "TEXT"),
    ("ngay_dang_tai", "TEXT"),
    ("so_quyet_dinh", "TEXT"),
    ("ngay_ban_hanh", "TEXT"),
    ("so_nha_thau", "TEXT"),
    ("dia_diem", "TEXT"),
]

VI_THUOC_HEADERS = [
    "STT", "Tên vị thuốc cổ truyền", "Bộ phận dùng", "Tên khoa học",
    "Nguồn gốc", "Phương pháp chế biến", "Số ĐKLH/Giấy phép NK",
    "Tên cơ sở sản xuất", "Nước sản xuất", "Quy cách đóng gói",
    "Đơn vị tính", "Số lượng", "Đơn giá trúng thầu", "Nhóm TCKT",
    "Mã TBMT", "Tên CĐT", "Hình thức LCNT", "Ngày đăng tải KQLCNT",
    "Số quyết định", "Ngày ban hành quyết định", "Số nhà thầu tham dự",
    "Địa điểm"
]

# ============================================================
# SCHEMA: Bảo hiểm xã hội (BHXH)
# ============================================================
BHXH_COLUMNS = [
    ("ma_tinh", "TEXT"),
    ("ten_tinh", "TEXT"),
    ("ten_don_vi", "TEXT"),
    ("ma_co_so_kcb", "TEXT"),
    ("ten_thuoc", "TEXT"),
    ("hoat_chat", "TEXT"),
    ("duong_dung", "TEXT"),
    ("dang_bao_che", "TEXT"),
    ("ham_luong", "TEXT"),
    ("dong_goi", "TEXT"),
    ("so_dang_ky", "TEXT"),
    ("nha_san_xuat", "TEXT"),
    ("nuoc_san_xuat", "TEXT"),
    ("don_vi_tinh", "TEXT"),
    ("so_luong", "TEXT"),
    ("gia", "TEXT"),
    ("thanh_tien", "TEXT"),
    ("ten_nha_thau", "TEXT"),
    ("quyet_dinh", "TEXT"),
    ("ngay_cong_bo", "TEXT"),
    ("nhom_tckt", "TEXT"),
    ("loai_thuoc", "TEXT"),
]

BHXH_HEADERS = [
    "Mã tỉnh", "Tên tỉnh", "Tên đơn vị", "Mã cơ sở KCB",
    "Tên thuốc", "Hoạt chất", "Đường dùng", "Dạng bào chế",
    "Hàm lượng", "Đóng gói", "Số đăng ký", "Nhà sản xuất",
    "Nước sản xuất", "Đơn vị tính", "Số lượng", "Giá",
    "Thành tiền", "Tên nhà thầu", "Quyết định", "Ngày công bố",
    "Nhóm TCKT", "Loại thuốc"
]

# ============================================================
# Mapping bảng → schema
# ============================================================
TABLE_SCHEMAS = {
    "thuoc_generic": THUOC_GENERIC_COLUMNS,
    "thuoc_biet_duoc": THUOC_BIET_DUOC_COLUMNS,
    "thuoc_duoc_lieu": THUOC_DUOC_LIEU_COLUMNS,
    "duoc_lieu": DUOC_LIEU_COLUMNS,
    "vi_thuoc": VI_THUOC_COLUMNS,
    "bhxh": BHXH_COLUMNS,
}

TABLE_HEADERS = {
    "thuoc_generic": THUOC_GENERIC_HEADERS,
    "thuoc_biet_duoc": THUOC_BIET_DUOC_HEADERS,
    "thuoc_duoc_lieu": THUOC_DUOC_LIEU_HEADERS,
    "duoc_lieu": DUOC_LIEU_HEADERS,
    "vi_thuoc": VI_THUOC_HEADERS,
    "bhxh": BHXH_HEADERS,
}

TABLE_DISPLAY_NAMES = {
    "thuoc_generic": "Thuốc Generic",
    "thuoc_biet_duoc": "Thuốc Biệt dược gốc",
    "thuoc_duoc_lieu": "Thuốc Dược liệu",
    "duoc_lieu": "Dược liệu",
    "vi_thuoc": "Vị thuốc cổ truyền",
    "bhxh": "Bảo hiểm xã hội",
}


class DatabaseManager:
    """Quản lý cơ sở dữ liệu SQLite cho ứng dụng Tra Cứu Giá Thuốc."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "thuoc.db")
        self.db_path = db_path
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Tạo connection mới."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_database(self):
        """Tạo tất cả các bảng nếu chưa có."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            for table_name, columns in TABLE_SCHEMAS.items():
                cols_sql = ", ".join(
                    f"{col_name} {col_type}" for col_name, col_type in columns
                )
                cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS {table_name} "
                    f"(id INTEGER PRIMARY KEY AUTOINCREMENT, {cols_sql})"
                )
            conn.commit()
        finally:
            conn.close()

    def import_from_excel(self, table_name: str, file_path: str,
                          sheet_name: Optional[str] = None) -> int:
        """Import dữ liệu từ file Excel vào bảng SQLite. Returns: số dòng đã import."""
        columns = TABLE_SCHEMAS.get(table_name)
        if columns is None:
            raise ValueError(f"Bảng '{table_name}' không tồn tại")

        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, dtype=str)
        else:
            df = pd.read_excel(file_path, sheet_name=sheet_name or 0, dtype=str)

        col_names = [col_name for col_name, _ in columns]
        num_cols = min(len(df.columns), len(col_names))
        df_subset = df.iloc[:, :num_cols]
        df_subset.columns = col_names[:num_cols]
        df_subset = df_subset.fillna("")

        conn = self._get_connection()
        try:
            conn.execute(f"DELETE FROM {table_name}")
            placeholders = ", ".join(["?"] * num_cols)
            insert_cols = ", ".join(col_names[:num_cols])
            sql = f"INSERT INTO {table_name} ({insert_cols}) VALUES ({placeholders})"
            rows = df_subset.values.tolist()
            conn.executemany(sql, rows)
            conn.commit()
            return len(rows)
        finally:
            conn.close()

    def get_all_data(self, table_name: str) -> list:
        """Lấy tất cả dữ liệu từ bảng."""
        conn = self._get_connection()
        try:
            columns = TABLE_SCHEMAS.get(table_name, [])
            col_names = ", ".join(col_name for col_name, _ in columns)
            cursor = conn.execute(f"SELECT {col_names} FROM {table_name}")
            return cursor.fetchall()
        finally:
            conn.close()

    def search_data(self, table_name: str, keyword: str,
                    filters: Optional[list] = None,
                    search_column: Optional[str] = None,
                    date_filters: Optional[dict] = None,
                    limit: Optional[int] = None,
                    offset: Optional[int] = None,
                    sort_column: Optional[str] = None,
                    sort_order: str = 'ASC') -> list:
        """Tìm kiếm dữ liệu trong bảng.
        filters: list of (col_name, value)
        date_filters: {'column': 'ngay_ban_hanh', 'start': 'dd/mm/yyyy', 'end': 'dd/mm/yyyy'}
        limit: số lượng bản ghi trả về (None = all)
        offset: vị trí bắt đầu
        """
        columns = TABLE_SCHEMAS.get(table_name, [])
        col_names = [col_name for col_name, _ in columns]
        select_cols = ", ".join(col_names)

        conditions = []
        params = []

        if keyword and keyword.strip():
            # Normalize keyword: remove spaces, lowercase for matching
            clean_keyword = keyword.replace(" ", "").lower()
            
            if search_column and search_column in col_names:
                conditions.append(f"LOWER(REPLACE({search_column}, ' ', '')) LIKE ?")
                params.append(f"%{clean_keyword}%")
            else:
                keyword_conditions = []
                for col_name in col_names:
                    # Apply logic to all columns
                    keyword_conditions.append(f"LOWER(REPLACE({col_name}, ' ', '')) LIKE ?")
                    params.append(f"%{clean_keyword}%")
                conditions.append(f"({' OR '.join(keyword_conditions)})")

        if filters:
            # Chuyen dict thanh list tuples neu can
            if isinstance(filters, dict):
                filter_items = filters.items()
            else:
                filter_items = filters

            for col_name, value in filter_items:
                if value and value.strip() and col_name in col_names:
                    # Also apply to advanced filters
                    clean_val = value.replace(" ", "").lower()
                    conditions.append(f"LOWER(REPLACE({col_name}, ' ', '')) LIKE ?")
                    params.append(f"%{clean_val}%")
        
        # Date Filter Logic
        if date_filters:
            col = date_filters.get('column')
            start = date_filters.get('start') # dd/mm/yyyy
            end = date_filters.get('end')     # dd/mm/yyyy
            
            if col and col in col_names and (start or end):
                # Convert stored DD/MM/YYYY to YYYY-MM-DD for comparison
                # Note: substr in sqlite is 1-based index
                # dd/mm/yyyy -> substr(col,7,4)||'-'||substr(col,4,2)||'-'||substr(col,1,2)
                
                parts = []
                # Ensure column has enough length (10 chars) before trying to substring
                date_sql = f"(length({col}) >= 10 AND substr({col},7,4) || '-' || substr({col},4,2) || '-' || substr({col},1,2)"
                
                if start:
                    # Convert input start dd/mm/yyyy -> yyyy-mm-dd
                    try:
                        d, m, y = start.split('/')
                        start_iso = f"{y}-{m}-{d}"
                        conditions.append(f"{date_sql} >= ?)")
                        params.append(start_iso)
                    except ValueError:
                        pass # Ignore invalid date format inputs
                        
                if end:
                    try:
                        d, m, y = end.split('/')
                        end_iso = f"{y}-{m}-{d}"
                        conditions.append(f"{date_sql} <= ?)")
                        params.append(end_iso)
                    except ValueError:
                        pass

        sql = f"SELECT id, {select_cols} FROM {table_name}"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        if sort_column and sort_column in col_names:
            # Validate sort_order
            order = 'DESC' if sort_order.upper() == 'DESC' else 'ASC'
            
            # Numeric columns that need integer sorting
            # 'stt' is definitely numeric
            if sort_column == 'stt':
                sql += f" ORDER BY CAST({sort_column} AS INTEGER) {order}"
            else:
                sql += f" ORDER BY {sort_column} {order}"
        else:
            # Default sort (e.g. by id desc or whatever makes sense, maybe specific logic per table?)
            # For now, let's default to id DESC if no sort, or just no order (which means insertion order usually)
            # Actually, consistent order is good for pagination.
            sql += " ORDER BY id ASC"


        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)
            if offset is not None:
                sql += " OFFSET ?"
                params.append(offset)

        conn = self._get_connection()
        try:
            cursor = conn.execute(sql, params)
            return cursor.fetchall()
        finally:
            conn.close()

    def get_data_by_ids(self, table_name: str, ids: list) -> list:
        """Lấy dữ liệu theo danh sách IP."""
        if not ids:
            return []
            
        columns = TABLE_SCHEMAS.get(table_name, [])
        col_names = ", ".join(col_name for col_name, _ in columns)
        
        placeholders = ", ".join(["?"] * len(ids))
        sql = f"SELECT {col_names} FROM {table_name} WHERE id IN ({placeholders})"
        
        conn = self._get_connection()
        try:
            cursor = conn.execute(sql, ids)
            return cursor.fetchall()
        finally:
            conn.close()

    def count_search_data(self, table_name: str, keyword: str,
                          filters: Optional[list] = None,
                          search_column: Optional[str] = None,
                          date_filters: Optional[dict] = None) -> int:
        """Đếm số kết quả tìm kiếm (không apply paginaton)."""
        columns = TABLE_SCHEMAS.get(table_name, [])
        col_names = [col_name for col_name, _ in columns]

        conditions = []
        params = []

        if keyword and keyword.strip():
            clean_keyword = keyword.replace(" ", "").lower()
            
            if search_column and search_column in col_names:
                conditions.append(f"LOWER(REPLACE({search_column}, ' ', '')) LIKE ?")
                params.append(f"%{clean_keyword}%")
            else:
                keyword_conditions = []
                for col_name in col_names:
                    keyword_conditions.append(f"LOWER(REPLACE({col_name}, ' ', '')) LIKE ?")
                    params.append(f"%{clean_keyword}%")
                conditions.append(f"({' OR '.join(keyword_conditions)})")

        if filters:
            if isinstance(filters, dict):
                filter_items = filters.items()
            else:
                filter_items = filters

            for col_name, value in filter_items:
                if value and value.strip() and col_name in col_names:
                    clean_val = value.replace(" ", "").lower()
                    conditions.append(f"LOWER(REPLACE({col_name}, ' ', '')) LIKE ?")
                    params.append(f"%{clean_val}%")

        if date_filters:
            col = date_filters.get('column')
            start = date_filters.get('start')
            end = date_filters.get('end')
            
            if col and col in col_names and (start or end):
                date_sql = f"(length({col}) >= 10 AND substr({col},7,4) || '-' || substr({col},4,2) || '-' || substr({col},1,2)"
                
                if start:
                    try:
                        d, m, y = start.split('/')
                        start_iso = f"{y}-{m}-{d}"
                        conditions.append(f"{date_sql} >= ?)")
                        params.append(start_iso)
                    except ValueError:
                        pass
                        
                if end:
                    try:
                        d, m, y = end.split('/')
                        end_iso = f"{y}-{m}-{d}"
                        conditions.append(f"{date_sql} <= ?)")
                        params.append(end_iso)
                    except ValueError:
                        pass

        sql = f"SELECT COUNT(*) FROM {table_name}"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        conn = self._get_connection()
        try:
            cursor = conn.execute(sql, params)
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def get_distinct_values(self, table_name: str, column_name: str) -> list:
        """Lấy danh sách giá trị distinct của 1 cột (cho ComboBox filter)."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                f"SELECT DISTINCT {column_name} FROM {table_name} "
                f"WHERE {column_name} IS NOT NULL AND {column_name} != '' "
                f"ORDER BY {column_name}"
            )
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_row_count(self, table_name: str) -> int:
        """Đếm số dòng trong bảng."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def delete_all_data(self, table_name: str):
        """Xóa toàn bộ dữ liệu trong bảng."""
        conn = self._get_connection()
        try:
            conn.execute(f"DELETE FROM {table_name}")
            conn.commit()
        finally:
            conn.close()

    def replace_all_data(self, table_name: str, rows: list):
        """Thay thế toàn bộ dữ liệu trong bảng (dùng cho sync từ Supabase)."""
        columns = TABLE_SCHEMAS.get(table_name)
        if columns is None:
            raise ValueError(f"Bảng '{table_name}' không tồn tại")

        col_names = [col_name for col_name, _ in columns]
        conn = self._get_connection()
        try:
            conn.execute(f"DELETE FROM {table_name}")
            if rows:
                placeholders = ", ".join(["?"] * len(col_names))
                insert_cols = ", ".join(col_names)
                sql = f"INSERT INTO {table_name} ({insert_cols}) VALUES ({placeholders})"
                conn.executemany(sql, rows)
            conn.commit()
        finally:
            conn.close()

    def export_to_excel(self, table_name: str, file_path: str,
                        data: Optional[list] = None):
        """Export dữ liệu ra file Excel."""
        headers = TABLE_HEADERS.get(table_name, [])
        if data is None:
            data = self.get_all_data(table_name)

        df = pd.DataFrame(data, columns=headers)
        if file_path.endswith('.csv'):
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
        else:
            df.to_excel(file_path, index=False, engine='openpyxl')

    def get_price_statistics(self, table_name: str, criteria: dict) -> dict:
        """
        Lấy thống kê giá (Min, Max, Count) dựa trên tiêu chí search chính xác.
        criteria: dictionary {column_name: value}
        """
        columns = TABLE_SCHEMAS.get(table_name)
        if not columns:
            return {'min': 0, 'max': 0, 'count': 0}

        col_names = [c[0] for c in columns]
        
        conditions = []
        params = []
        
        for col, val in criteria.items():
            if col in col_names and val:
                # Use scalar function for case-insensitive matching if needed, 
                # but for exact match requirement "lower()" is safer.
                conditions.append(f"LOWER(TRIM({col})) = ?")
                params.append(str(val).strip().lower())
                
        if not conditions:
            return {'min': 0, 'max': 0, 'count': 0}
            
        where_clause = " AND ".join(conditions)
        
        # Determine price column based on table
        # Default 'don_gia' for drugs, 'don_gia_trung_thau' for herbal/others
        price_col = 'don_gia'
        if 'don_gia_trung_thau' in col_names:
            price_col = 'don_gia_trung_thau'
        elif 'gia' in col_names:
            price_col = 'gia'
            
        sql = f"""
            SELECT 
                MIN(CAST(REPLACE(REPLACE({price_col}, ',', ''), '.', '') AS INTEGER)),
                MAX(CAST(REPLACE(REPLACE({price_col}, ',', ''), '.', '') AS INTEGER)),
                COUNT(*)
            FROM {table_name}
            WHERE {where_clause}
        """
        
        conn = self._get_connection()
        try:
            cursor = conn.execute(sql, params)
            row = cursor.fetchone()
            if row:
                return {
                    'min': row[0] or 0,
                    'max': row[1] or 0,
                    'count': row[2] or 0
                }
            return {'min': 0, 'max': 0, 'count': 0}
        finally:
            conn.close()

