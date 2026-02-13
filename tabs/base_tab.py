"""
BaseTab - Class cơ sở cho tất cả tab trong ứng dụng Tra Cứu Giá Thuốc.
Cung cấp: search bar, bộ lọc, QTableWidget, import/export, sync Supabase.
"""

import statistics
import math
from typing import Optional, List, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QMessageBox, QFileDialog,
    QGroupBox, QProgressBar, QApplication, QGridLayout,
    QDateEdit, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QDate
from PyQt6.QtGui import QColor, QAction

from database import DatabaseManager, TABLE_HEADERS, TABLE_SCHEMAS
from supabase_manager import SupabaseDataManager
from theme_manager import ThemeManager


class SyncWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, table_name: str):
        super().__init__()
        self.table_name = table_name

    def run(self):
        try:
            manager = SupabaseDataManager()
            data = manager.pull_table_data(self.table_name, list(range(50))) # Demo pull, logic inside manager handles full pull
            # Note: actual manager.pull_table_data implementation might vary, 
            # assuming it returns list of values matching schema.
            # Re-checking logic if necessary.
            # Use fetch_all for full sync
            data = manager.fetch_all(self.table_name)
            self.finished.emit(data)
        except Exception as e:
            self.error.emit(str(e))


class BaseTab(QWidget):
    TABLE_NAME = ""       # Override in subclass
    TAB_TITLE = ""        # Override in subclass
    FILTER_COLUMNS = []   # Override in subclass if using legacy filters (now unused)
    SEARCH_COLUMNS = []   # Override in subclass for search dropdown
    PRICE_COLUMN = "don_gia" # Default price column

    def __init__(self, db: DatabaseManager, is_admin: bool = False, parent=None):
        super().__init__(parent)
        self.db = db
        self.is_admin = is_admin
        if self.TABLE_NAME:
            self.headers = ["Chọn"] + TABLE_HEADERS.get(self.TABLE_NAME, [])
        else:
            self.headers = []

        self.current_data = []
        self._sync_worker = None
        
        # Pagination State
        self.current_page = 1
        self.page_size = 50
        self.total_records = 0
        self.current_search_params = {} # Store active search params
        self.selected_ids = set() # Store selected row IDs
        
        # Sorting State
        self.current_sort_column = None
        self.current_sort_order = "ASC"

        
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self.apply_theme)

        self._setup_ui()
        self.table.itemChanged.connect(self._on_item_changed)
        self._load_data()

    def _setup_ui(self):
        """Thiết lập giao diện."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # ===== HEADER ROW =====
        header_layout = QHBoxLayout()

        title_label = QLabel(f"\U0001f4cb {self.TAB_TITLE}")
        title_label.setObjectName("titleLabel")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.count_label = QLabel("Tong: 0 dong")
        self.count_label.setObjectName("countLabel")
        header_layout.addWidget(self.count_label)

        layout.addLayout(header_layout)

        # ===== SEARCH BAR (dropdown + input) =====
        self.search_frame = QFrame()
        self.search_frame.setObjectName("searchFrame")
        
        search_inner = QHBoxLayout(self.search_frame)
        search_inner.setContentsMargins(4, 4, 4, 4)
        search_inner.setSpacing(0)

        # Column selector dropdown
        self.search_column_combo = QComboBox()
        self.search_column_combo.setObjectName("searchColumnCombo")
        self.search_column_combo.addItem("TAT CA", "")  # empty = all columns
        # Add columns from SEARCH_COLUMNS or default from headers
        if self.SEARCH_COLUMNS:
            for display_name, db_col in self.SEARCH_COLUMNS:
                self.search_column_combo.addItem(display_name, db_col)
        else:
            # Fallback: use first few important columns from schema
            columns = TABLE_SCHEMAS.get(self.TABLE_NAME, [])
            headers_list = TABLE_HEADERS.get(self.TABLE_NAME, [])
            for i, (col_name, _) in enumerate(columns[:6]):
                if i < len(headers_list) and col_name != "stt":
                    self.search_column_combo.addItem(headers_list[i], col_name)

        self.search_column_combo.setMinimumWidth(120)
        self.search_column_combo.setFixedHeight(36)
        self.search_column_combo.currentIndexChanged.connect(
            self._on_search_column_changed
        )
        search_inner.addWidget(self.search_column_combo)

        # Separator line
        self.separator = QFrame()
        self.separator.setFixedWidth(1)
        self.separator.setFixedHeight(24)
        search_inner.addWidget(self.separator)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self._update_search_placeholder()
        self.search_input.setClearButtonEnabled(True)
        self.search_input.returnPressed.connect(self._perform_search)
        search_inner.addWidget(self.search_input, 1)

        # Search button - main action
        self.search_btn = QPushButton("Tim kiem")
        self.search_btn.setObjectName("searchBtn")
        self.search_btn.setFixedHeight(32)
        self.search_btn.setFixedWidth(120)
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_btn.clicked.connect(self._perform_search)
        search_inner.addWidget(self.search_btn)



        layout.addWidget(self.search_frame)

        # ===== FILTER GROUP (Dynamic) =====
        filter_group = QGroupBox("Bo loc nang cao")
        filter_group_layout = QVBoxLayout()
        filter_group_layout.setSpacing(10)

        # Date Range Filter
        date_filter_row = QHBoxLayout()
        
        self.chk_date_filter = QCheckBox("Lọc theo ngày ban hành")
        self.chk_date_filter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_date_filter.toggled.connect(self._toggle_date_filter)
        date_filter_row.addWidget(self.chk_date_filter)
        
        date_filter_row.addSpacing(10)
        
        date_filter_row.addWidget(QLabel("Từ:"))
        self.date_edit_start = QDateEdit()
        self.date_edit_start.setCalendarPopup(True)
        self.date_edit_start.setDisplayFormat("dd/MM/yyyy")
        self.date_edit_start.setDate(QDate.currentDate().addMonths(-1))
        self.date_edit_start.setEnabled(False)
        self.date_edit_start.setFixedWidth(110)
        date_filter_row.addWidget(self.date_edit_start)
        
        date_filter_row.addWidget(QLabel("Đến:"))
        self.date_edit_end = QDateEdit()
        self.date_edit_end.setCalendarPopup(True)
        self.date_edit_end.setDisplayFormat("dd/MM/yyyy")
        self.date_edit_end.setDate(QDate.currentDate())
        self.date_edit_end.setEnabled(False)
        self.date_edit_end.setFixedWidth(110)
        date_filter_row.addWidget(self.date_edit_end)
        
        date_filter_row.addStretch()
        filter_group_layout.addLayout(date_filter_row)

        separator_filter = QFrame()
        separator_filter.setFrameShape(QFrame.Shape.HLine)
        separator_filter.setFrameShadow(QFrame.Shadow.Sunken)
        filter_group_layout.addWidget(separator_filter)

        # Container for filter rows
        self.filter_rows_container = QWidget()
        self.filter_rows_layout = QVBoxLayout(self.filter_rows_container)
        self.filter_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.filter_rows_layout.setSpacing(8)
        self.filter_rows_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        filter_group_layout.addWidget(self.filter_rows_container)

        # "Add Condition" button
        self.add_filter_btn = QPushButton("+ Them dieu kien")
        self.add_filter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_filter_btn.clicked.connect(self._add_filter_row)
        
        # Button row for Add/Clear
        filter_btn_row = QHBoxLayout()
        filter_btn_row.setContentsMargins(0, 0, 0, 0)
        
        filter_btn_row.addWidget(self.add_filter_btn)
        
        # "Clear Filters" button
        self.clear_filters_btn = QPushButton("Xóa bộ lọc")
        self.clear_filters_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_filters_btn.clicked.connect(self._clear_all_filters)
        filter_btn_row.addWidget(self.clear_filters_btn)
        
        filter_btn_row.addStretch()
        
        filter_group_layout.addLayout(filter_btn_row)

        filter_group.setLayout(filter_group_layout)
        layout.addWidget(filter_group)

        # Init list to store filter widgets
        self.filter_rows = [] 
        
        # Mapping display -> db column
        self.col_map_display_to_db = {}
        self.col_map_db_to_display = {}
        
        schema = TABLE_SCHEMAS.get(self.TABLE_NAME, [])
        headers_list = TABLE_HEADERS.get(self.TABLE_NAME, [])
        for i, (col_db, _) in enumerate(schema):
            if i < len(headers_list):
                display = headers_list[i]
                self.col_map_display_to_db[display] = col_db
                self.col_map_db_to_display[col_db] = display

    # ---------- Action Buttons ----------
        btn_layout = QHBoxLayout()

        # Sync button (always visible)
        sync_btn = QPushButton("🔄 Cập nhật dữ liệu")
        sync_btn.setObjectName("syncBtn")
        sync_btn.clicked.connect(self._sync_from_supabase)
        btn_layout.addWidget(sync_btn)

        # Admin-only buttons
        if self.is_admin:
            import_btn = QPushButton("📥 Import Excel")
            import_btn.setObjectName("importBtn")
            import_btn.clicked.connect(self._import_excel)
            btn_layout.addWidget(import_btn)

        if self.is_admin:
            push_btn = QPushButton("☁️ Đẩy lên Supabase")
            push_btn.setObjectName("pushBtn")
            push_btn.clicked.connect(self._push_to_supabase)
            btn_layout.addWidget(push_btn)

        export_selected_btn = QPushButton("☑ Xuất Đã Chọn")
        export_selected_btn.setObjectName("exportSelectedBtn")
        export_selected_btn.clicked.connect(self._export_selected_excel)
        btn_layout.addWidget(export_selected_btn)

        export_btn = QPushButton("📤 Export Excel (All)")
        export_btn.setObjectName("exportBtn")
        export_btn.clicked.connect(self._export_excel)
        btn_layout.addWidget(export_btn)

        btn_layout.addStretch()

        if self.is_admin:
            delete_btn = QPushButton("🗑 Xóa dữ liệu")
            delete_btn.setObjectName("deleteDataBtn")
            delete_btn.clicked.connect(self._delete_data)
            btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)

        # ===== STATISTICS BAR =====
        # ===== STATISTICS CARDS =====
        stats_container = QWidget()
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setContentsMargins(0, 5, 0, 10)
        stats_layout.setSpacing(15)

        # Create cards (labels will be styled by apply_theme)
        def create_card_widget(title, object_name):
            card = QFrame()
            card.setObjectName(object_name)
            card.setFrameShape(QFrame.Shape.StyledPanel)
            card.setFrameShadow(QFrame.Shadow.Raised)
            
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 10, 10, 10)
            card_layout.setSpacing(2)
            
            lbl_title = QLabel(title)
            lbl_title.setObjectName("cardTitle")
            lbl_title.setStyleSheet("font-size: 11px; font-weight: 600; text-transform: uppercase;")
            card_layout.addWidget(lbl_title)
            
            lbl_value = QLabel("0")
            lbl_value.setObjectName("cardValue")
            lbl_value.setStyleSheet("font-size: 18px; font-weight: bold;")
            lbl_value.setAlignment(Qt.AlignmentFlag.AlignLeft)
            card_layout.addWidget(lbl_value)
            
            return card, lbl_value

        # 1. Total
        self.card_total, self.lbl_val_total = create_card_widget("TỔNG SỐ", "cardTotal")
        stats_layout.addWidget(self.card_total)

        # 2. Min
        self.card_min, self.lbl_val_min = create_card_widget("GIÁ THẤP NHẤT", "cardMin")
        stats_layout.addWidget(self.card_min)

        # 3. Mean
        self.card_mean, self.lbl_val_mean = create_card_widget("TRUNG BÌNH", "cardMean")
        stats_layout.addWidget(self.card_mean)

        # 4. Median
        self.card_median, self.lbl_val_median = create_card_widget("TRUNG VỊ", "cardMedian")
        stats_layout.addWidget(self.card_median)

        # 5. Max
        self.card_max, self.lbl_val_max = create_card_widget("GIÁ CAO NHẤT", "cardMax")
        stats_layout.addWidget(self.card_max)



        layout.addWidget(stats_container)

        # Move pagination container to after the table
        # We need to remove it from current position (before table) and add it after
        pass



        # ===== SYNC STATUS =====
        self.sync_status_label = QLabel("")
        self.sync_status_label.setObjectName("syncStatusLabel")
        self.sync_status_label.setVisible(False)
        layout.addWidget(self.sync_status_label)

        # ===== PROGRESS BAR =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # ===== TABLE =====
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # Disable client-side sorting to handle server-side sorting (pagination)
        self.table.setSortingEnabled(False)

        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setDefaultSectionSize(130)

        # Column widths
        # Column widths
        for i in range(len(self.headers)):
            if i == 0: # Checkbox column
                self.table.setColumnWidth(i, 40)
            elif i == 1:  # STT (now index 1)
                self.table.setColumnWidth(i, 50)
            elif i == 2:  # Tên thuốc / Tên dược liệu
                self.table.setColumnWidth(i, 250)
            elif i == 3:
                self.table.setColumnWidth(i, 220)

        # Column widths
        for i in range(len(self.headers)):
            if i == 0: # Checkbox column
                self.table.setColumnWidth(i, 40)
            elif i == 1:  # STT (now index 1)
                self.table.setColumnWidth(i, 50)
            elif i == 2:  # Tên thuốc / Tên dược liệu
                self.table.setColumnWidth(i, 250)
            elif i == 3:
                self.table.setColumnWidth(i, 220)

        # Connect header click for Select All
        self.table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)

        layout.addWidget(self.table, 1)

        # ===== PAGINATION CONTROLS (Below Table) =====
        self.pagination_container = QWidget()
        pag_layout = QHBoxLayout(self.pagination_container)
        pag_layout.setContentsMargins(0, 5, 0, 5)
        pag_layout.setSpacing(5) # Reduced spacing
        pag_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Style for small buttons
        btn_style = """
            QPushButton {
                font-size: 11px;
                padding: 4px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """

        self.btn_first_page = QPushButton("⏮") # Unicode First Track
        self.btn_first_page.setFixedWidth(30)
        self.btn_first_page.setToolTip("Trang đầu")
        self.btn_first_page.setStyleSheet(btn_style)
        self.btn_first_page.clicked.connect(self._on_first_page)
        pag_layout.addWidget(self.btn_first_page)

        self.btn_prev_page = QPushButton("◀") # Unicode Previous
        self.btn_prev_page.setFixedWidth(30)
        self.btn_prev_page.setToolTip("Trang trước")
        self.btn_prev_page.setStyleSheet(btn_style)
        self.btn_prev_page.clicked.connect(self._on_prev_page)
        pag_layout.addWidget(self.btn_prev_page)

        self.lbl_page_info = QLabel("Trang 0/0")
        self.lbl_page_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_page_info.setFixedWidth(100)
        self.lbl_page_info.setStyleSheet("font-size: 11px; font-weight: bold;")
        pag_layout.addWidget(self.lbl_page_info)

        self.btn_next_page = QPushButton("▶") # Unicode Next
        self.btn_next_page.setFixedWidth(30)
        self.btn_next_page.setToolTip("Trang sau")
        self.btn_next_page.setStyleSheet(btn_style)
        self.btn_next_page.clicked.connect(self._on_next_page)
        pag_layout.addWidget(self.btn_next_page)

        self.btn_last_page = QPushButton("⏭") # Unicode Last Track
        self.btn_last_page.setFixedWidth(30)
        self.btn_last_page.setToolTip("Trang cuối")
        self.btn_last_page.setStyleSheet(btn_style)
        self.btn_last_page.clicked.connect(self._on_last_page)
        pag_layout.addWidget(self.btn_last_page)

        layout.addWidget(self.pagination_container)

        # Apply initial theme
        self.apply_theme(self.theme_manager.get_theme())

    def _add_filter_row(self):
        """Them mot dong loc moi."""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        # Column select
        col_combo = QComboBox()
        col_combo.setMinimumWidth(180)
        
        # Populate combos with all headers (except STT usually)
        for display, db_col in self.col_map_display_to_db.items():
            if db_col != 'stt':
                col_combo.addItem(display, db_col)
        
        row_layout.addWidget(col_combo)

        # Value input
        val_input = QLineEdit()
        val_input.setPlaceholderText("Nhap gia tri tim kiem...")
        val_input.returnPressed.connect(self._perform_search)
        row_layout.addWidget(val_input, 1)

        # Remove button
        remove_btn = QPushButton("X")
        remove_btn.setFixedSize(24, 24)
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Use closure to capture row_widget
        remove_btn.clicked.connect(lambda: self._remove_filter_row(row_widget))
        row_layout.addWidget(remove_btn)

        self.filter_rows_layout.addWidget(row_widget)
        
        # Store widgets for later retrieval
        row_data = {
            'widget': row_widget,
            'combo': col_combo,
            'input': val_input,
            'remove_btn': remove_btn
        }
        self.filter_rows.append(row_data)
        
        # Apply theme to this new row
        self._style_filter_row(row_data, self.theme_manager.get_theme())

    def _remove_filter_row(self, row_widget):
        """Xoa mot dong loc."""
        for i, row in enumerate(self.filter_rows):
            if row['widget'] == row_widget:
                self.filter_rows_layout.removeWidget(row_widget)
                row_widget.deleteLater()
                self.filter_rows.pop(i)
                break

    # ---------- Search & Filter ----------

    def _update_search_placeholder(self):
        """Cap nhat placeholder theo cot dang chon."""
        idx = self.search_column_combo.currentIndex()
        if idx == 0:
            self.search_input.setPlaceholderText(
                "Nhap tu khoa tim kiem tren tat ca cot..."
            )
        else:
            col_name = self.search_column_combo.currentText()
            self.search_input.setPlaceholderText(
                f"Tim kiem theo {col_name}..."
            )

    def _on_search_column_changed(self, index):
        self._update_search_placeholder()

    def _get_active_filters(self) -> list:
        """Lay danh sach cac bo loc dang active."""
        filters = []
        for row in self.filter_rows:
            col_display = row['combo'].currentText()
            col_db = self.col_map_display_to_db.get(col_display)
            value = row['input'].text().strip()
            
            if col_db and value:
                filters.append((col_db, value))
        return filters

    def _get_search_column(self) -> str:
        """Lay cot dang chon de tim kiem. Tra ve '' neu 'TAT CA'."""
        return self.search_column_combo.currentData() or ""

    def _toggle_date_filter(self, checked):
        self.date_edit_start.setEnabled(checked)
        self.date_edit_end.setEnabled(checked)
        # Trigger search immediately? Maybe not, let user click search.
        # But if unchecking, we might want to re-search? 
        # For consistency with other filters (that wait for search btn usually, except clear), let's wait.
    
    def _perform_search(self):
        keyword = self.search_input.text().strip()
        filters = self._get_active_filters()
        search_col = self._get_search_column()
        
        date_filters = None
        if self.chk_date_filter.isChecked():
            date_filters = {
                'column': 'ngay_ban_hanh',
                'start': self.date_edit_start.date().toString("dd/MM/yyyy"),
                'end': self.date_edit_end.date().toString("dd/MM/yyyy")
            }
            
        # Update current search params
        self.current_search_params = {
            'keyword': keyword,
            'filters': filters,
            'search_column': search_col if search_col else None,
            'date_filters': date_filters
        }
        
        self.current_page = 1
        self._load_current_page()

    def _load_data(self):
        # Initial load: empty params -> all data
        self.current_search_params = {
            'keyword': "",
            'filters': [],
            'search_column': None,
            'date_filters': None
        }
        self.current_page = 1
        self._load_current_page()

    def _load_current_page(self):
        """Load data for current page using current_search_params."""
        params = self.current_search_params
        
        # 1. Count total records
        self.total_records = self.db.count_search_data(
            self.TABLE_NAME, 
            keyword=params.get('keyword'),
            filters=params.get('filters'),
            search_column=params.get('search_column'),
            date_filters=params.get('date_filters')
        )
        
        # 2. Calculate offset
        offset = (self.current_page - 1) * self.page_size
        
        # 3. Fetch page data
        data = self.db.search_data(
            self.TABLE_NAME,
            keyword=params.get('keyword'),
            filters=params.get('filters'),
            search_column=params.get('search_column'),
            date_filters=params.get('date_filters'),
            limit=self.page_size,
            offset=offset,
            sort_column=self.current_sort_column,
            sort_order=self.current_sort_order
        )

        
        self.current_data = data # This is page data now
        self._populate_table(data)
        self._update_pagination_ui()

    def _update_pagination_ui(self):
        total_pages = math.ceil(self.total_records / self.page_size) if self.page_size > 0 else 1
        if total_pages < 1: total_pages = 1
        
        self.lbl_page_info.setText(f"Trang {self.current_page}/{total_pages}")
        
        self.btn_first_page.setEnabled(self.current_page > 1)
        self.btn_prev_page.setEnabled(self.current_page > 1)
        self.btn_next_page.setEnabled(self.current_page < total_pages)
        self.btn_last_page.setEnabled(self.current_page < total_pages)
        
        # Update count label to show range
        if self.total_records > 0:
            start = (self.current_page - 1) * self.page_size + 1
            end = min(self.current_page * self.page_size, self.total_records)
            self.count_label.setText(
                f"Hiển thị: {start:,}-{end:,} / Tổng: {self.total_records:,} dòng"
            )
        else:
             self.count_label.setText("Tổng: 0 dòng")

    def _on_first_page(self):
        if self.current_page > 1:
            self.current_page = 1
            self._load_current_page()

    def _on_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._load_current_page()

    def _on_next_page(self):
        total_pages = math.ceil(self.total_records / self.page_size)
        if self.current_page < total_pages:
            self.current_page += 1
            self._load_current_page()

    def _on_last_page(self):
        total_pages = math.ceil(self.total_records / self.page_size)
        if self.current_page < total_pages:
            self.current_page = total_pages
            self._load_current_page()

    def _calculate_stats(self, data: list):
        """Tính toán và hiển thị thống kê."""
        total_count = len(data)
        prices = []
        
        # Tim index cua cot gia
        price_col_idx = -1
        schema = TABLE_SCHEMAS.get(self.TABLE_NAME, [])
        for i, (col_db, _) in enumerate(schema):
            if col_db == self.PRICE_COLUMN:
                price_col_idx = i
                break
        
        if price_col_idx != -1:
            for row in data:
                if price_col_idx < len(row):
                    val_raw = row[price_col_idx]
                    if val_raw:
                        # Parse price string (remove non-digits except maybe decimal separator if meaningful)
                        # Assuming VND is integer usually or using comma/dot separators
                        # Simple approach: keep only digits
                        digits = "".join(filter(str.isdigit, str(val_raw)))
                        if digits:
                            prices.append(int(digits))

        if prices:
            p_min = min(prices)
            p_max = max(prices)
            p_mean = statistics.mean(prices)
            p_median = statistics.median(prices)
            
            self.lbl_val_min.setText(f"{p_min:,.0f}")
            self.lbl_val_mean.setText(f"{p_mean:,.0f}")
            self.lbl_val_median.setText(f"{p_median:,.0f}")
            self.lbl_val_max.setText(f"{p_max:,.0f}")
        else:
            self.lbl_val_min.setText("0")
            self.lbl_val_mean.setText("0")
            self.lbl_val_median.setText("0")
            self.lbl_val_max.setText("0")
            
        self.lbl_val_total.setText(f"{total_count:,}")

    def _populate_table(self, data: list):
        # We need data for stats, but data now includes ID at index 0
        # _calculate_stats expects data without ID or we adjust it.
        # Let's adjust data passed to stats by stripping ID
        data_no_id = [row[1:] for row in data] if data else []
        self._calculate_stats(data_no_id)
        
        self.table.blockSignals(True) # Block signals to prevent _on_item_changed during populate
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        self.table.setRowCount(len(data))

        for row_idx, full_row in enumerate(data):
            row_id = full_row[0]
            row_data = full_row[1:]
            
            # Checkbox column first
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            
            if row_id in self.selected_ids:
                checkbox_item.setCheckState(Qt.CheckState.Checked)
            else:
                checkbox_item.setCheckState(Qt.CheckState.Unchecked)
                
            checkbox_item.setData(Qt.ItemDataRole.UserRole, row_id) # Store ID
            self.table.setItem(row_idx, 0, checkbox_item)
            
            for col_idx, value in enumerate(row_data):
                # Data columns shifted by 1
                item = QTableWidgetItem(str(value) if value else "")
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
                )
                self.table.setItem(row_idx, col_idx + 1, item)

        # self.table.setSortingEnabled(True) # Do NOT re-enable client-side sorting
        self.table.blockSignals(False)


        # Label updated in _update_pagination_ui now
        pass

    def _on_item_changed(self, item):
        """Handle checkbox toggle."""
        if item.column() == 0:
            row_id = item.data(Qt.ItemDataRole.UserRole)
            if row_id is not None:
                if item.checkState() == Qt.CheckState.Checked:
                    self.selected_ids.add(row_id)
                else:
                    self.selected_ids.discard(row_id)

    def _on_header_clicked(self, index):
        """Toggle all checkboxes on current page when header 0 is clicked."""
        if index == 0:
            row_count = self.table.rowCount()
            if row_count == 0:
                return

            # Check if all are currently checked
            all_checked = True
            for i in range(row_count):
                item = self.table.item(i, 0)
                if item.checkState() == Qt.CheckState.Unchecked:
                    all_checked = False
                    break
            
            # Toggle state
            target_state = Qt.CheckState.Unchecked if all_checked else Qt.CheckState.Checked
            
            # Apply to all rows
            # Note: setting checkState will trigger itemChanged signal -> updates selected_ids
            for i in range(row_count):
                item = self.table.item(i, 0)
                if item.checkState() != target_state:
                    item.setCheckState(target_state)

        else:
            # Sort content by column
            # Map index to DB column
            # Index 0 is checkbox, so data cols start at index 1
            # But headers list includes "Chọn" at 0.
            # TABLE_SCHEMAS/HEADERS maps correctly?
            # self.headers = ["Chọn"] + TABLE_HEADERS...
            
            # Map header index to DB schema index
            # Header 1 -> Schema 0
            # Header 2 -> Schema 1
            
            schema_idx = index - 1
            if schema_idx < 0: return

            schema = TABLE_SCHEMAS.get(self.TABLE_NAME, [])
            if schema_idx < len(schema):
                col_db_name = schema[schema_idx][0]
                
                # Toggle sort order if same column
                if self.current_sort_column == col_db_name:
                    self.current_sort_order = "DESC" if self.current_sort_order == "ASC" else "ASC"
                else:
                    self.current_sort_column = col_db_name
                    self.current_sort_order = "ASC"
                
                self._update_header_visuals()
                self._load_current_page()

    def _update_header_visuals(self):
        """Update headers to show sort indicators."""
        for i in range(self.table.columnCount()):
            # Get original text from self.headers
            if i < len(self.headers):
                original_text = self.headers[i]
                
                # Check if this is the sorted column
                # Map index i to db column
                is_sorted = False
                if i > 0:
                    schema_idx = i - 1
                    schema = TABLE_SCHEMAS.get(self.TABLE_NAME, [])
                    if schema_idx < len(schema):
                        col_db_name = schema[schema_idx][0]
                        if col_db_name == self.current_sort_column:
                            is_sorted = True
                            indicator = " \u25B2" if self.current_sort_order == "ASC" else " \u25BC" # ▲ / ▼
                            new_text = f"{original_text}{indicator}"
                            item = QTableWidgetItem(new_text)
                            self.table.setHorizontalHeaderItem(i, item)
                            continue
                
                # Reset others
                if self.table.horizontalHeaderItem(i).text() != original_text:
                     self.table.setHorizontalHeaderItem(i, QTableWidgetItem(original_text))


    def _clear_all_filters(self):
        self.chk_date_filter.setChecked(False)
        self.search_input.clear()
        self.search_column_combo.blockSignals(True)
        self.search_column_combo.setCurrentIndex(0)
        self.search_column_combo.blockSignals(False)
        self._update_search_placeholder()
        
        # Clear filter rows
        while self.filter_rows:
            row_data = self.filter_rows.pop()
            widget = row_data['widget']
            self.filter_rows_layout.removeWidget(widget)
            widget.deleteLater()
            
        self._perform_search()

    # ---------- Supabase Sync ----------

    def _sync_from_supabase(self):
        """Tải dữ liệu từ Supabase về SQLite."""
        reply = QMessageBox.question(
            self, "Cập nhật dữ liệu",
            f"Tải dữ liệu {self.TAB_TITLE} từ server về?\n"
            "Dữ liệu cũ trong máy sẽ được thay thế.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.sync_status_label.setText("⏳ Đang tải dữ liệu từ server...")
        self.sync_status_label.setVisible(True)

        self._sync_worker = SyncWorker(self.TABLE_NAME)
        self._sync_worker.progress.connect(self._on_sync_progress)
        self._sync_worker.finished.connect(self._on_sync_finished)
        self._sync_worker.error.connect(self._on_sync_error)
        self._sync_worker.start()

    def _on_sync_progress(self, count):
        self.sync_status_label.setText(
            f"⏳ Đang tải... đã nhận {count:,} dòng"
        )

    def _on_sync_finished(self, data):
        self.progress_bar.setVisible(False)
        self.sync_status_label.setVisible(False)

        try:
            self.db.replace_all_data(self.TABLE_NAME, data)
            self._load_data()
            QMessageBox.information(
                self, "Thành công",
                f"Đã cập nhật {len(data):,} dòng dữ liệu {self.TAB_TITLE}."
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Lỗi", f"Lỗi lưu dữ liệu:\n{str(e)}"
            )

    def _on_sync_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.sync_status_label.setVisible(False)
        QMessageBox.critical(
            self, "Lỗi cập nhật",
            f"Không thể tải dữ liệu từ server:\n{error_msg}"
        )

    # ---------- Push to Supabase (Admin) ----------

    def _push_to_supabase(self):
        """Đẩy dữ liệu từ SQLite lên Supabase (admin only)."""
        total = self.db.get_row_count(self.TABLE_NAME)
        if total == 0:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu để đẩy lên!")
            return

        reply = QMessageBox.question(
            self, "Đẩy dữ liệu lên server",
            f"Đẩy {total:,} dòng dữ liệu {self.TAB_TITLE} lên server?\n"
            "Dữ liệu cũ trên server sẽ được thay thế.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, total)
        self.sync_status_label.setText("☁️ Đang đẩy dữ liệu lên server...")
        self.sync_status_label.setVisible(True)
        QApplication.processEvents()

        try:
            data = self.db.get_all_data(self.TABLE_NAME)
            manager = SupabaseDataManager()

            def progress_cb(pushed, total_rows):
                self.progress_bar.setValue(pushed)
                self.sync_status_label.setText(
                    f"☁️ Đang đẩy... {pushed:,}/{total_rows:,} dòng"
                )
                QApplication.processEvents()

            count = manager.push_table_data(
                self.TABLE_NAME, data, progress_callback=progress_cb
            )

            self.progress_bar.setVisible(False)
            self.sync_status_label.setVisible(False)
            QMessageBox.information(
                self, "Thành công",
                f"Đã đẩy {count:,} dòng dữ liệu lên server!"
            )
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.sync_status_label.setVisible(False)
            QMessageBox.critical(
                self, "Lỗi", f"Không thể đẩy dữ liệu:\n{str(e)}"
            )

    # ---------- Import / Export / Delete ----------

    def _import_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file Excel để import", "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
        )
        if not file_path:
            return

        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            QApplication.processEvents()

            count = self.db.import_from_excel(self.TABLE_NAME, file_path)

            self.progress_bar.setVisible(False)
            self._load_data()

            QMessageBox.information(
                self, "Thành công",
                f"Đã import {count:,} dòng dữ liệu vào bảng {self.TAB_TITLE}."
            )
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(
                self, "Lỗi Import", f"Không thể import file:\n{str(e)}"
            )

    def _export_excel(self):
        if not self.current_data:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu để export!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu file Excel",
            f"{self.TAB_TITLE}.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        if not file_path:
            return

        try:
            # Export ALL matching data
            # search_data now returns (id, ...) so we need to strip index 0
            params = self.current_search_params
            data_with_id = self.db.search_data(
                self.TABLE_NAME,
                keyword=params.get('keyword'),
                filters=params.get('filters'),
                search_column=params.get('search_column'),
                date_filters=params.get('date_filters'),
                limit=None,
                offset=None
            )
            
            data = [row[1:] for row in data_with_id]
            
            self.db.export_to_excel(self.TABLE_NAME, file_path, data)
            QMessageBox.information(
                self, "Thành công",
                f"Đã export {len(data):,} dòng ra file:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Lỗi Export", f"Không thể export file:\n{str(e)}"
            )

    def _export_selected_excel(self):
        """Export selected rows (persisted across pages)."""
        if not self.selected_ids:
             QMessageBox.warning(self, "Cảnh báo", "Chưa chọn dòng nào để export!")
             return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu file Excel (Đã chọn)",
            f"{self.TAB_TITLE}_selected.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        if not file_path:
            return

        try:
            # Fetch data by IDs
            selected_rows_data = self.db.get_data_by_ids(self.TABLE_NAME, list(self.selected_ids))
            
            self.db.export_to_excel(self.TABLE_NAME, file_path, selected_rows_data)
            QMessageBox.information(
                self, "Thành công",
                f"Đã export {len(selected_rows_data):,} dòng đã chọn ra file:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Lỗi Export", f"Không thể export file:\n{str(e)}"
            )

    def apply_theme(self, theme):
        """Apply theme to local widgets."""
        # Search Frame
        self.search_frame.setStyleSheet(f"""
            #searchFrame {{
                background-color: {theme['input_bg']};
                border: 2px solid {theme['border']};
                border-radius: 10px;
            }}
            #searchFrame:focus-within {{
                border-color: {theme['border_focus']};
            }}
        """)
        
        # Search Column Combo
        self.search_column_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {theme['widget_bg']};
                color: {theme['text_main']};
                border: none;
                border-radius: 7px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 700;
                font-family: "Segoe UI";
                min-width: 100px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {theme['text_dim']};
                margin-right: 6px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme['widget_bg']};
                color: {theme['text_main']};
                border: 1px solid {theme['border']};
                selection-background-color: {theme['selection_bg']};
                padding: 4px;
            }}
        """)

        # Separator
        self.separator.setStyleSheet(f"background-color: {theme['border']};")
        
        # Search Input
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                color: {theme['text_main']};
                border: none;
                padding: 8px 12px;
                font-size: 14px;
                font-family: "Segoe UI";
            }}
            QLineEdit::placeholder {{
                color: {theme['input_placeholder']};
            }}
        """)

        # Search Button (using primary gradient if available or primary/accent)
        # Using a simple gradient based on primary color
        self.search_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme['primary']}, stop:1 {theme['border_focus']}
                );
                color: #ffffff;
                border: none;
                border-radius: 7px;
                font-size: 13px;
                font-weight: 700;
                margin-right: 4px;
                font-family: "Segoe UI";
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme['primary_hover']}, stop:1 {theme['accent']}
                );
            }}
        """)

        # Filter Buttons
        self.add_filter_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['widget_bg']};
                color: {theme['text_dim']};
                border: 1px dashed {theme['border']};
                border-radius: 6px;
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: {theme['input_bg']};
                color: {theme['border_focus']};
                border-color: {theme['border_focus']};
            }}
        """)

        self.clear_filters_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['grid_line']};
                color: {theme['text_dim']};
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme['border']};
                color: {theme['text_main']};
            }}
        """)

        # Stats Cards
        self._style_card(self.card_total, theme['card_total_start'], theme['card_total_end'])
        self._style_card(self.card_min, theme['card_min_start'], theme['card_min_end'])
        self._style_card(self.card_mean, theme['card_mean_start'], theme['card_mean_end'])
        self._style_card(self.card_median, theme['card_median_start'], theme['card_median_end'])
        self._style_card(self.card_max, theme['card_max_start'], theme['card_max_end'])

        # Date Filter Styles
        self.chk_date_filter.setStyleSheet(f"color: {theme['text_main']};")
        
        date_edit_style = f"""
            QDateEdit {{
                background-color: {theme['input_bg']};
                color: {theme['text_main']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 4px;
            }}
            QDateEdit::drop-down {{
                border: none;
                width: 20px;
            }}
            QDateEdit::down-arrow {{
                image: none;
                border: none;
                /* Maybe use a custom icon or just simple arrow similar to combo */
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {theme['text_dim']};
                margin-right: 2px;
            }}
            QDateEdit::disabled {{
                background-color: {theme['app_bg']};
                color: {theme['text_dim']};
                border-color: {theme['border']};
            }}
        """
        self.date_edit_start.setStyleSheet(date_edit_style)
        self.date_edit_start.setStyleSheet(date_edit_style)
        self.date_edit_end.setStyleSheet(date_edit_style)

        # Pagination Buttons
        # Note: We used inline style in _setup_ui, but good to have theme awareness here if we want to change colors dynamically.
        # Since I set inline style with hardcoded colors in _setup_ui, I should override it here OR update _setup_ui to not use hardcoded colors.
        # Let's update the keys in the inline style to use theme variables.
        # However, since they are QPushButtons without object names, I can't target them easily via stylesheet here unless I kept references (which I did: self.btn_first_page etc).
        
        pag_btn_style = f"""
            QPushButton {{
                font-size: 11px;
                padding: 4px;
                border: 1px solid {theme['border']};
                border-radius: 4px;
                background-color: {theme['widget_bg']};
                color: {theme['text_main']};
            }}
            QPushButton:hover {{
                background-color: {theme['input_bg']};
                border-color: {theme['border_focus']};
            }}
            QPushButton:disabled {{
                color: {theme['text_dim']};
                background-color: {theme['app_bg']};
                border-color: {theme['border']};
            }}
        """
        self.btn_first_page.setStyleSheet(pag_btn_style)
        self.btn_prev_page.setStyleSheet(pag_btn_style)
        self.btn_next_page.setStyleSheet(pag_btn_style)
        self.btn_last_page.setStyleSheet(pag_btn_style)
        
        self.lbl_page_info.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme['text_main']};")

        # Filter Rows (if any)
        for row in self.filter_rows:
            self._style_filter_row(row, theme)
            
    def _style_card(self, card, start, end):
        # Retrieve current theme text colors
        theme = self.theme_manager.get_theme()
        text_dim = theme.get('text_dim', '#8899aa')
        
        card.setStyleSheet(f"""
            QFrame#{card.objectName()} {{
                background-color: transparent;
                border: 2px solid {start};
                border-radius: 8px;
            }}
            QLabel#cardTitle {{
                color: {text_dim};
                background-color: transparent;
            }}
            QLabel#cardValue {{
                color: {start};
                background-color: transparent;
            }}
        """)

    def _style_filter_row(self, row_data, theme):
        # Combo
        row_data['combo'].setStyleSheet(f"""
            QComboBox {{
                padding: 4px;
                background-color: {theme['input_bg']};
                color: {theme['text_main']};
                border: 1px solid {theme['border']};
            }}
        """)
        # Input
        row_data['input'].setStyleSheet(f"""
            QLineEdit {{
                padding: 4px;
                background-color: {theme['input_bg']};
                color: {theme['text_main']};
                border: 1px solid {theme['border']};
            }}
        """)
        # Remove Btn (if it's in row_data, but current structure might not have it exposed easily)
        # Actually _add_filter_row doesn't store the button in row_data dict.
        # I should probably update _add_filter_row to store it first.

    def _delete_data(self):
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc muốn xóa TOÀN BỘ dữ liệu trong bảng {self.TAB_TITLE}?\n\n"
            "Hành động này không thể hoàn tác!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_all_data(self.TABLE_NAME)
            self._load_data()
            QMessageBox.information(
                self, "Đã xóa",
                f"Đã xóa toàn bộ dữ liệu trong bảng {self.TAB_TITLE}."
            )

class SyncWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, table_name):
        super().__init__()
        self.table_name = table_name

    def run(self):
        try:
            manager = SupabaseDataManager()
            data = manager.fetch_table_data(self.table_name, progress_callback=self.progress.emit)
            self.finished.emit(data)
        except Exception as e:
            self.error.emit(str(e))
