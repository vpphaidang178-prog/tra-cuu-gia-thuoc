"""
User Manager - Quan ly tai khoan nguoi dung (Admin only)
Tao tai khoan bang username/password, khong can email
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QApplication,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QFormLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from auth.supabase_client import SupabaseAuth


class UserManagerDialog(QDialog):
    """Dialog quan ly tai khoan (Admin only)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth = SupabaseAuth()
        self._setup_ui()
        self._apply_styles()
        self._load_users()

    def _setup_ui(self):
        self.setWindowTitle("Quan ly tai khoan")
        self.setMinimumSize(700, 560)
        self.setModal(True)

        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(
                (geo.width() - 700) // 2,
                (geo.height() - 560) // 2,
            )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Title
        title = QLabel("Quan ly tai khoan")
        title.setObjectName("dialogTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # ===== USER LIST =====
        list_group = QGroupBox("Danh sach tai khoan")
        list_layout = QVBoxLayout()

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(
            ["Tai khoan", "Ten hien thi", "Vai tro", "Ngay tao"]
        )
        self.user_table.setAlternatingRowColors(True)
        self.user_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.user_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.user_table.verticalHeader().setVisible(False)
        header = self.user_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        list_layout.addWidget(self.user_table)

        # Buttons under table
        table_btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Lam moi")
        refresh_btn.clicked.connect(self._load_users)
        table_btn_layout.addWidget(refresh_btn)

        table_btn_layout.addStretch()

        delete_btn = QPushButton("Xoa tai khoan")
        delete_btn.setObjectName("deleteBtn")
        delete_btn.clicked.connect(self._delete_selected)
        table_btn_layout.addWidget(delete_btn)
        list_layout.addLayout(table_btn_layout)

        list_group.setLayout(list_layout)
        layout.addWidget(list_group, 1)

        # ===== CREATE FORM =====
        form_group = QGroupBox("Tao tai khoan moi")
        form_layout = QHBoxLayout()
        form_layout.setSpacing(10)

        self.new_username = QLineEdit()
        self.new_username.setPlaceholderText("Tai khoan")
        self.new_username.setMinimumHeight(38)
        form_layout.addWidget(self.new_username, 1)

        self.new_display = QLineEdit()
        self.new_display.setPlaceholderText("Ten hien thi")
        self.new_display.setMinimumHeight(38)
        form_layout.addWidget(self.new_display, 1)

        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Mat khau")
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password.setMinimumHeight(38)
        form_layout.addWidget(self.new_password, 1)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        self.role_combo.setMinimumHeight(38)
        self.role_combo.setMinimumWidth(90)
        form_layout.addWidget(self.role_combo)

        create_btn = QPushButton("Tao")
        create_btn.setObjectName("createBtn")
        create_btn.setMinimumHeight(38)
        create_btn.setMinimumWidth(80)
        create_btn.clicked.connect(self._create_user)
        form_layout.addWidget(create_btn)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # ===== STATUS =====
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Close button
        close_btn = QPushButton("Dong")
        close_btn.setMinimumHeight(36)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog { background-color: #1a1a2e; color: #e0e0e0; font-family: "Segoe UI"; }
            #dialogTitle { color: #ffffff; }

            QGroupBox {
                border: 1px solid #0f3460; border-radius: 8px;
                margin-top: 12px; padding: 14px; padding-top: 22px;
                font-weight: 600; color: #8899aa;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 14px; padding: 0 6px;
            }

            QTableWidget {
                background-color: #16213e; color: #e0e0e0;
                border: 1px solid #0f3460; border-radius: 6px;
                gridline-color: #0f3460; font-size: 12px;
            }
            QTableWidget::item { padding: 6px; }
            QTableWidget::item:selected { background-color: #0f3460; }
            QHeaderView::section {
                background-color: #0f3460; color: #ffffff;
                padding: 6px; border: none; font-weight: 600;
            }

            QLineEdit {
                background-color: #16213e; color: #e0e0e0;
                border: 1.5px solid #0f3460; border-radius: 8px;
                padding: 8px 12px; font-size: 13px;
            }
            QLineEdit:focus { border: 1.5px solid #667eea; }

            QComboBox {
                background-color: #16213e; color: #e0e0e0;
                border: 1.5px solid #0f3460; border-radius: 8px;
                padding: 8px 12px; font-size: 13px;
            }
            QComboBox QAbstractItemView {
                background-color: #16213e; color: #e0e0e0;
                border: 1px solid #0f3460;
                selection-background-color: #0f3460;
            }

            QLabel { color: #c0d0e0; font-size: 12px; }

            QPushButton {
                background-color: #2a3a5a; color: #e0e0e0; border: none;
                border-radius: 8px; font-size: 13px; font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #3a4a6a; }

            #createBtn {
                background-color: #0a8a4a; color: white; font-weight: 700;
            }
            #createBtn:hover { background-color: #0caa5a; }

            #deleteBtn {
                background-color: #c0392b; color: white; font-weight: 700;
            }
            #deleteBtn:hover { background-color: #e74c3c; }
        """)

    def _load_users(self):
        """Load danh sach tai khoan."""
        users = self.auth.get_all_users()
        self.user_table.setRowCount(0)
        self.user_table.setRowCount(len(users))

        for row, user in enumerate(users):
            self.user_table.setItem(
                row, 0, QTableWidgetItem(user.get("username", ""))
            )
            self.user_table.setItem(
                row, 1, QTableWidgetItem(user.get("display_name", ""))
            )
            role = user.get("role", "user")
            role_item = QTableWidgetItem(role.upper())
            self.user_table.setItem(row, 2, role_item)
            created = user.get("created_at", "")[:10]
            self.user_table.setItem(row, 3, QTableWidgetItem(created))

    def _create_user(self):
        username = self.new_username.text().strip()
        display_name = self.new_display.text().strip()
        password = self.new_password.text()
        role = self.role_combo.currentText()

        if not username or not password or not display_name:
            self.status_label.setText("Vui long dien day du thong tin!")
            self.status_label.setStyleSheet("color: #e94560;")
            return

        if len(password) < 6:
            self.status_label.setText("Mat khau phai co toi thieu 6 ky tu!")
            self.status_label.setStyleSheet("color: #e94560;")
            return

        self.status_label.setText("Dang tao...")
        self.status_label.setStyleSheet("color: #667eea;")
        QApplication.processEvents()

        success, message = self.auth.create_user(
            username, password, display_name, role
        )

        if success:
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: #0caa5a;")
            self.new_username.clear()
            self.new_display.clear()
            self.new_password.clear()
            self.role_combo.setCurrentIndex(0)
            self._load_users()
        else:
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: #e94560;")

    def _delete_selected(self):
        row = self.user_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chu y", "Vui long chon tai khoan can xoa!")
            return

        username = self.user_table.item(row, 0).text()

        reply = QMessageBox.question(
            self, "Xac nhan xoa",
            f"Ban co chac muon xoa tai khoan '{username}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        success, message = self.auth.delete_user(username)
        if success:
            self.status_label.setText(f"Da xoa tai khoan '{username}'")
            self.status_label.setStyleSheet("color: #0caa5a;")
            self._load_users()
        else:
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: #e94560;")
