"""Tab: Thuoc Biet duoc goc (Mua sam cong)"""
from tabs.base_tab import BaseTab


class BietDuocTab(BaseTab):
    TABLE_NAME = "thuoc_biet_duoc"
    TAB_TITLE = "Thuoc Biet duoc goc"
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
