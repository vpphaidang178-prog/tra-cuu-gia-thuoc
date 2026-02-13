"""
Dialog cho phép tìm kiếm và chọn một dòng dữ liệu từ các bảng thuốc.
Sử dụng logic tương tự BaseTab nhưng trong QDialog.
"""

import math
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from database import DatabaseManager, TABLE_HEADERS, TABLE_SCHEMAS

class SearchSelectionDialog(QDialog):
    def __init__(self, db: DatabaseManager, table_name: str, initial_keyword: str = "", parent=None):
        super().__init__(parent)
        self.db = db
        self.table_name = table_name
        
        # Setup configs based on table
        self.headers = TABLE_HEADERS.get(self.table_name, [])
        self.schema = TABLE_SCHEMAS.get(self.table_name, [])
        
        self.selected_data = None # Store result
        
        # Pagination
        self.current_page = 1
        self.page_size = 20
        self.total_records = 0
        self.current_keyword = initial_keyword
        
        self._setup_ui()
        self.search_input.setText(initial_keyword)
        self._load_data()

    def _setup_ui(self):
        self.setWindowTitle("Chọn thuốc để đối chiếu")
        self.resize(1000, 600)
        
        layout = QVBoxLayout(self)
        
        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập từ khóa tìm kiếm...")
        self.search_input.returnPressed.connect(self._load_data)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Tìm kiếm")
        search_btn.clicked.connect(self._load_data)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._on_double_click)
        
        layout.addWidget(self.table)
        
        # Pagination
        pag_layout = QHBoxLayout()
        self.btn_prev = QPushButton("<")
        self.btn_prev.clicked.connect(self._prev_page)
        pag_layout.addWidget(self.btn_prev)
        
        self.lbl_page = QLabel("1/1")
        self.lbl_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pag_layout.addWidget(self.lbl_page)
        
        self.btn_next = QPushButton(">")
        self.btn_next.clicked.connect(self._next_page)
        pag_layout.addWidget(self.btn_next)
        
        layout.addLayout(pag_layout)
        
        # Dialog Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        
        self.btn_select = QPushButton("Chọn")
        self.btn_select.clicked.connect(self._on_select)
        self.btn_select.setEnabled(False) # Enable when row selected
        btn_box.addWidget(self.btn_select)
        
        self.btn_close = QPushButton("Đóng")
        self.btn_close.clicked.connect(self.reject)
        btn_box.addWidget(self.btn_close)
        
        layout.addLayout(btn_box)
        
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

    def _load_data(self):
        self.current_keyword = self.search_input.text().strip()
        
        # Count
        self.total_records = self.db.count_search_data(
            self.table_name,
            keyword=self.current_keyword
        )
        
        # Data
        offset = (self.current_page - 1) * self.page_size
        data = self.db.search_data(
            self.table_name,
            keyword=self.current_keyword,
            limit=self.page_size,
            offset=offset
        )
        
        self._populate_table(data)
        self._update_pagination()

    def _populate_table(self, data):
        self.table.setRowCount(0)
        self.table.setRowCount(len(data))
        self.current_data = data # Store for retrieval
        
        for r, row in enumerate(data):
            # row[0] is ID, data starts at 1
            row_data = row[1:]
            for c, val in enumerate(row_data):
                item = QTableWidgetItem(str(val) if val else "")
                self.table.setItem(r, c, item)

    def _update_pagination(self):
        total_pages = math.ceil(self.total_records / self.page_size) or 1
        self.lbl_page.setText(f"{self.current_page}/{total_pages}")
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < total_pages)

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._load_data()

    def _next_page(self):
        total_pages = math.ceil(self.total_records / self.page_size) or 1
        if self.current_page < total_pages:
            self.current_page += 1
            self._load_data()

    def _on_selection_changed(self):
        self.btn_select.setEnabled(bool(self.table.selectedItems()))

    def _on_double_click(self):
        self._on_select()

    def _on_select(self):
        row_idx = self.table.currentRow()
        if row_idx >= 0 and row_idx < len(self.current_data):
            # Return the full row data (including ID at 0 if needed, or mapped dict)
            # Let's return the row data tuple from DB
            self.selected_data = self.current_data[row_idx]
            self.accept()
        else:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một dòng dữ liệu.")
