"""Tab: Duoc lieu (nguyen lieu tho)"""
from tabs.base_tab import BaseTab


class DuocLieuRawTab(BaseTab):
    TABLE_NAME = "duoc_lieu"
    TAB_TITLE = "Duoc lieu (Raw)"
    PRICE_COLUMN = "don_gia_trung_thau"
    SEARCH_COLUMNS = [
        ("Ten duoc lieu", "ten_duoc_lieu"),
        ("Ten khoa hoc", "ten_khoa_hoc"),
        ("Co so san xuat", "ten_co_so_san_xuat"),
        ("Don gia", "don_gia_trung_thau"),
    ]
    FILTER_COLUMNS = [
        ("Nhom TCKT", "nhom_tckt"),
        ("Nguon goc", "nguon_goc"),
        ("Nuoc san xuat", "nuoc_san_xuat"),
    ]
