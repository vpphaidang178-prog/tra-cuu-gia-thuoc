"""Tab: Bao hiem xa hoi (BHXH)"""
from tabs.base_tab import BaseTab


class BHXHTab(BaseTab):
    TABLE_NAME = "bhxh"
    TAB_TITLE = "Bao hiem xa hoi"
    PRICE_COLUMN = "gia"
    SEARCH_COLUMNS = [
        ("Ten thuoc", "ten_thuoc"),
        ("Hoat chat", "hoat_chat"),
        ("So dang ky", "so_dang_ky"),
        ("Nha san xuat", "nha_san_xuat"),
        ("Gia", "gia"),
    ]
    FILTER_COLUMNS = [
        ("Ten tinh", "ten_tinh"),
        ("Nhom TCKT", "nhom_tckt"),
        ("Loai thuoc", "loai_thuoc"),
        ("Nuoc san xuat", "nuoc_san_xuat"),
    ]
