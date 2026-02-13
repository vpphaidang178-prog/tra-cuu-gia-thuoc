"""Tab: Thuoc Generic (Mua sam cong)"""
from tabs.base_tab import BaseTab


class GenericTab(BaseTab):
    TABLE_NAME = "thuoc_generic"
    TAB_TITLE = "Thuoc Generic"
    SEARCH_COLUMNS = [
        ("Ten thuoc", "ten_thuoc"),
        ("Hoat chat", "ten_hoat_chat"),
        ("So GPLH", "gdklh"),
        ("Co so san xuat", "ten_co_so_san_xuat"),
        ("Don gia", "don_gia"),
    ]
    FILTER_COLUMNS = [
        ("Nhom thuoc", "nhom_thuoc"),
        ("Duong dung", "duong_dung"),
        ("Dang bao che", "dang_bao_che"),
        ("Nuoc san xuat", "nuoc_san_xuat"),
    ]

