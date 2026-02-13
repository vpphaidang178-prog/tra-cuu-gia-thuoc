"""Tab: Vi thuoc co truyen"""
from tabs.base_tab import BaseTab


class ViThuocTab(BaseTab):
    TABLE_NAME = "vi_thuoc"
    TAB_TITLE = "Vi thuoc co truyen"
    PRICE_COLUMN = "don_gia_trung_thau"
    SEARCH_COLUMNS = [
        ("Ten vi thuoc", "ten_vi_thuoc"),
        ("Ten khoa hoc", "ten_khoa_hoc"),
        ("Co so san xuat", "ten_co_so_san_xuat"),
        ("Don gia", "don_gia_trung_thau"),
    ]
    FILTER_COLUMNS = [
        ("Nhom TCKT", "nhom_tckt"),
        ("Nguon goc", "nguon_goc"),
        ("Nuoc san xuat", "nuoc_san_xuat"),
    ]
