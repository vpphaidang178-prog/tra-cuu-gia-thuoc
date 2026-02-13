"""
Data Uploader - Đẩy dữ liệu từ SQLite lên Supabase (Admin only)
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QMessageBox, QApplication,
    QProgressBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database import DatabaseManager, TABLE_DISPLAY_NAMES
from supabase_manager import SupabaseDataManager


class DataUploaderDialog(QDialog):
    """Dialog đẩy dữ liệu từ SQLite lên Supabase."""

    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self._setup_ui()
        self._apply_styles()
        self._update_preview()

    def _setup_ui(self):
        self.setWindowTitle("☁️ Đẩy dữ liệu lên Server")
        self.setMinimumSize(450, 350)
        self.setModal(True)

        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(
                (geo.width() - 450) // 2,
                (geo.height() - 350) // 2
            )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("☁️ Đẩy dữ liệu lên Supabase")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffffff;")
        layout.addWidget(title)

        # Table selection
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("📋 Chọn bảng dữ liệu:"))

        self.table_combo = QComboBox()
        for table_name, display_name in TABLE_DISPLAY_NAMES.items():
            self.table_combo.addItem(display_name, table_name)
        self.table_combo.currentIndexChanged.connect(self._update_preview)
        select_layout.addWidget(self.table_combo, 1)

        layout.addLayout(select_layout)

        # Preview info
        self.preview_label = QLabel("...")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet(
            "font-size: 14px; color: #7b2ff7; font-weight: 600; padding: 12px;"
        )
        layout.addWidget(self.preview_label)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.upload_btn = QPushButton("☁️ Đẩy lên Server")
        self.upload_btn.setObjectName("uploadBtn")
        self.upload_btn.setMinimumHeight(42)
        self.upload_btn.clicked.connect(self._upload)
        btn_layout.addWidget(self.upload_btn)

        upload_all_btn = QPushButton("🔄 Đẩy TẤT CẢ")
        upload_all_btn.setObjectName("uploadAllBtn")
        upload_all_btn.setMinimumHeight(42)
        upload_all_btn.clicked.connect(self._upload_all)
        btn_layout.addWidget(upload_all_btn)

        close_btn = QPushButton("❌ Đóng")
        close_btn.setMinimumHeight(42)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog { background-color: #1a1a2e; color: #e0e0e0; font-family: "Segoe UI"; }
            QLabel { color: #c0d0e0; font-size: 13px; }
            QComboBox {
                background-color: #16213e; color: #e0e0e0;
                border: 2px solid #0f3460; border-radius: 8px;
                padding: 10px 14px; font-size: 13px;
            }
            QComboBox QAbstractItemView {
                background-color: #16213e; color: #e0e0e0;
                border: 1px solid #0f3460;
                selection-background-color: #0f3460;
            }
            QProgressBar {
                background-color: #16213e; border: 1px solid #0f3460;
                border-radius: 6px; text-align: center; color: #ffffff;
                font-size: 11px; height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #7b2ff7, stop:1 #e94560);
                border-radius: 5px;
            }
            #uploadBtn {
                background-color: #e67e22; color: white; border: none;
                border-radius: 8px; font-size: 14px; font-weight: 700;
            }
            #uploadBtn:hover { background-color: #f39c12; }
            #uploadAllBtn {
                background-color: #7b2ff7; color: white; border: none;
                border-radius: 8px; font-size: 14px; font-weight: 700;
            }
            #uploadAllBtn:hover { background-color: #9b59f7; }
            QPushButton {
                background-color: #2a3a5a; color: #e0e0e0; border: none;
                border-radius: 8px; font-size: 14px; font-weight: 600;
            }
            QPushButton:hover { background-color: #3a4a6a; }
        """)

    def _update_preview(self):
        table_name = self.table_combo.currentData()
        if table_name:
            count = self.db.get_row_count(table_name)
            display = TABLE_DISPLAY_NAMES.get(table_name, table_name)
            self.preview_label.setText(
                f"📊 {display}: {count:,} dòng dữ liệu"
            )

    def _upload(self):
        """Đẩy bảng được chọn lên Supabase."""
        table_name = self.table_combo.currentData()
        display = TABLE_DISPLAY_NAMES.get(table_name, table_name)
        count = self.db.get_row_count(table_name)

        if count == 0:
            QMessageBox.warning(
                self, "Cảnh báo",
                f"Bảng {display} không có dữ liệu!"
            )
            return

        reply = QMessageBox.question(
            self, "Xác nhận",
            f"Đẩy {count:,} dòng dữ liệu {display} lên server?\n"
            "Dữ liệu cũ trên server sẽ được thay thế.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._do_upload(table_name)

    def _upload_all(self):
        """Đẩy tất cả bảng lên Supabase."""
        reply = QMessageBox.question(
            self, "Xác nhận",
            "Đẩy TẤT CẢ dữ liệu lên server?\nDữ liệu cũ sẽ được thay thế.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        for table_name in TABLE_DISPLAY_NAMES:
            count = self.db.get_row_count(table_name)
            if count > 0:
                self._do_upload(table_name)

        QMessageBox.information(self, "Hoàn tất", "Đã đẩy tất cả dữ liệu!")

    def _do_upload(self, table_name: str):
        display = TABLE_DISPLAY_NAMES.get(table_name, table_name)
        data = self.db.get_all_data(table_name)

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(data))
        self.status_label.setText(f"☁️ Đang đẩy {display}...")
        self.status_label.setVisible(True)
        QApplication.processEvents()

        try:
            manager = SupabaseDataManager()

            def progress_cb(pushed, total):
                self.progress_bar.setValue(pushed)
                self.status_label.setText(
                    f"☁️ {display}: {pushed:,}/{total:,} dòng"
                )
                QApplication.processEvents()

            manager.push_table_data(
                table_name, data, progress_callback=progress_cb
            )

            self.progress_bar.setVisible(False)
            self.status_label.setText(f"✅ {display}: {len(data):,} dòng đã đẩy!")
            self.status_label.setStyleSheet("color: #0caa5a; font-weight: 600;")

        except Exception as e:
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"❌ Lỗi: {str(e)}")
            self.status_label.setStyleSheet("color: #e94560;")
            QMessageBox.critical(
                self, "Lỗi", f"Không thể đẩy {display}:\n{str(e)}"
            )
