"""
Main Application Window - Tra Cứu Giá Thuốc
Menu-based navigation với QStackedWidget
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QStackedWidget, QStatusBar, QMenuBar,
    QApplication, QMessageBox, QLabel, QWidget, QVBoxLayout,
    QToolButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont

from database import DatabaseManager
from tabs.generic_tab import GenericTab
from tabs.biet_duoc_tab import BietDuocTab
from tabs.duoc_lieu_tab import DuocLieuTab
from tabs.duoc_lieu_raw_tab import DuocLieuRawTab
from tabs.vi_thuoc_tab import ViThuocTab
from tabs.bhxh_tab import BHXHTab
from styles import get_stylesheet
from theme_manager import ThemeManager
from auth.session import Session


class WelcomeWidget(QWidget):
    """Trang chào mừng khi khởi động app."""

    def __init__(self, session: Session, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Welcome title
        welcome = QLabel("💊 Tra Cứu Giá Thuốc")
        welcome.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
        layout.addWidget(welcome)

        # Subtitle
        subtitle = QLabel("Phần mềm tra cứu giá thuốc trúng thầu")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #8899aa;")
        layout.addWidget(subtitle)

        # User info
        role_emoji = "👑" if session.is_admin else "👤"
        user_info = QLabel(
            f"\n{role_emoji} Xin chào, {session.username}!"
        )
        user_info.setFont(QFont("Segoe UI", 16))
        user_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_info.setStyleSheet("color: #7b2ff7; margin-top: 20px;")
        layout.addWidget(user_info)

        # Instructions
        instructions = QLabel(
            "\n📌 Sử dụng menu Tra cứu để bắt đầu\n"
            "• Mua sắm công: Thuốc Generic, Biệt dược gốc, Dược liệu, Vị thuốc\n"
            "• Bảo hiểm xã hội: Dữ liệu BHXH"
        )
        instructions.setFont(QFont("Segoe UI", 12))
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("color: #667788; line-height: 1.6;")
        layout.addWidget(instructions)

        # Version
        version = QLabel("\nPhiên bản 2.0.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: #4a5a6a; font-size: 11px; margin-top: 30px;")
        layout.addWidget(version)


class MainWindow(QMainWindow):
    """Cửa sổ chính của ứng dụng Tra Cứu Giá Thuốc."""

    # Tab name mapping for status bar
    TAB_NAMES = {
        0: "Trang chủ",
        1: "Thuốc Generic",
        2: "Thuốc Biệt dược gốc",
        3: "Thuốc Dược liệu",
        4: "Dược liệu",
        5: "Vị thuốc cổ truyền",
        6: "Bảo hiểm xã hội",
    }

    def __init__(self, session: Session):
        super().__init__()
        self.session = session
        self.db = DatabaseManager()
        self.theme_manager = ThemeManager()
        self._setup_window()
        self._setup_menu()
        self._setup_pages()
        self._setup_statusbar()
        
        self.theme_manager.theme_changed.connect(self.apply_theme)
        self.apply_theme(self.theme_manager.get_theme())

    def apply_theme(self, theme):
        self.setStyleSheet(get_stylesheet(theme))

    def _setup_window(self):
        """Cấu hình cửa sổ chính."""
        self.setWindowTitle("💊 Tra Cứu Giá Thuốc - Kết quả đấu thầu")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 850)

        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            x = (screen_geo.width() - self.width()) // 2
            y = (screen_geo.height() - self.height()) // 2
            self.move(x, y)

    def _setup_menu(self):
        """Tạo menu bar với cấu trúc phân cấp."""
        menubar = self.menuBar()

        # ===== FILE MENU =====
        file_menu = menubar.addMenu("&File")

        about_action = QAction("ℹ️ Giới thiệu", self)
        about_action.triggered.connect(self._show_about)
        file_menu.addAction(about_action)

        file_menu.addSeparator()

        logout_action = QAction("🚪 Đăng xuất", self)
        logout_action.setShortcut("Ctrl+L")
        logout_action.triggered.connect(self._handle_logout)
        file_menu.addAction(logout_action)

        file_menu.addSeparator()

        exit_action = QAction("❌ Thoát", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ===== THEME TOGGLE (Corner Widget) =====
        self.theme_btn = QToolButton(self)
        self.theme_btn.setText("🌓")
        self.theme_btn.setToolTip("Chế độ Sáng/Tối")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(self.theme_manager.toggle_theme)
        
        # Style cho button đẹp hơn
        self.theme_btn.setStyleSheet("""
            QToolButton {
                border: none;
                border-radius: 4px;
                padding: 4px;
                font-size: 12pt;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)

        # Add to top-right corner
        menubar.setCornerWidget(self.theme_btn, Qt.Corner.TopRightCorner)

        # ===== TRA CỨU MENU =====
        lookup_menu = menubar.addMenu("&Tra cứu")

        # Sub-menu: Mua sắm công
        msc_menu = lookup_menu.addMenu("🏥 Mua sắm công")

        msc_items = [
            ("💊 Thuốc Generic", "Ctrl+1", 1),
            ("💎 Thuốc Biệt dược gốc", "Ctrl+2", 2),
            ("🌿 Thuốc Dược liệu", "Ctrl+3", 3),
            ("🌱 Dược liệu", "Ctrl+4", 4),
            ("🍃 Vị thuốc cổ truyền", "Ctrl+5", 5),
        ]
        for label, shortcut, index in msc_items:
            action = QAction(label, self)
            action.setShortcut(shortcut)
            action.triggered.connect(
                lambda checked, i=index: self._switch_page(i)
            )
            msc_menu.addAction(action)

        lookup_menu.addSeparator()

        # BHXH
        bhxh_action = QAction("🏦 Bảo hiểm xã hội", self)
        bhxh_action.setShortcut("Ctrl+6")
        bhxh_action.triggered.connect(lambda: self._switch_page(6))
        lookup_menu.addAction(bhxh_action)

        lookup_menu.addSeparator()

        # Search focus
        search_action = QAction("🔍 Tìm kiếm (Focus)", self)
        search_action.setShortcut("Ctrl+F")
        search_action.triggered.connect(self._focus_search)
        lookup_menu.addAction(search_action)

        # ===== QUẢN TRỊ MENU (Admin only) =====
        if self.session.is_admin:
            admin_menu = menubar.addMenu("&Quản trị")

            user_mgmt_action = QAction("👥 Quản lý tài khoản", self)
            user_mgmt_action.triggered.connect(self._show_user_manager)
            admin_menu.addAction(user_mgmt_action)

            admin_menu.addSeparator()

            data_upload_action = QAction("☁️ Đẩy dữ liệu lên Server", self)
            data_upload_action.triggered.connect(self._show_data_uploader)
            admin_menu.addAction(data_upload_action)

        # ===== KẾ HOẠCH LCNT MENU =====
        lcnt_menu = menubar.addMenu("📉 Kế hoạch LCNT")
        
        compare_action = QAction("Đối chiếu giá trúng thầu", self)
        compare_action.triggered.connect(self._show_compare_price)
        lcnt_menu.addAction(compare_action)

    def _show_compare_price(self):
        """Mở dialog đối chiếu giá."""
        from tabs.compare_price_dialog import ComparePriceDialog
        dialog = ComparePriceDialog(self.db, self)
        dialog.exec()

    def _setup_pages(self):
        """Tạo QStackedWidget với các trang."""
        self.stack = QStackedWidget()
        is_admin = self.session.is_admin

        # Index 0: Welcome page
        self.welcome_page = WelcomeWidget(self.session)
        self.stack.addWidget(self.welcome_page)

        # Index 1-5: Mua sắm công tabs
        self.tab_generic = GenericTab(self.db, is_admin)
        self.tab_biet_duoc = BietDuocTab(self.db, is_admin)
        self.tab_duoc_lieu = DuocLieuTab(self.db, is_admin)
        self.tab_duoc_lieu_raw = DuocLieuRawTab(self.db, is_admin)
        self.tab_vi_thuoc = ViThuocTab(self.db, is_admin)

        self.stack.addWidget(self.tab_generic)      # 1
        self.stack.addWidget(self.tab_biet_duoc)     # 2
        self.stack.addWidget(self.tab_duoc_lieu)      # 3
        self.stack.addWidget(self.tab_duoc_lieu_raw)  # 4
        self.stack.addWidget(self.tab_vi_thuoc)       # 5

        # Index 6: BHXH
        self.tab_bhxh = BHXHTab(self.db, is_admin)
        self.stack.addWidget(self.tab_bhxh)           # 6

        self.setCentralWidget(self.stack)

    def _setup_statusbar(self):
        """Tạo status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        role_emoji = "👑" if self.session.is_admin else "👤"
        self.statusbar.showMessage(
            f"Đăng nhập: {role_emoji} {self.session.username} "
            f"({self.session.role.upper()}) | Sẵn sàng tra cứu"
        )

    def _switch_page(self, index: int):
        """Chuyển trang hiển thị."""
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)
            tab_name = self.TAB_NAMES.get(index, "")
            role_emoji = "👑" if self.session.is_admin else "👤"
            self.statusbar.showMessage(
                f"Đăng nhập: {role_emoji} {self.session.username} "
                f"({self.session.role.upper()}) | Đang xem: {tab_name}"
            )

    def _focus_search(self):
        """Focus vào ô tìm kiếm của trang hiện tại."""
        current = self.stack.currentWidget()
        if hasattr(current, 'search_input'):
            current.search_input.setFocus()
            current.search_input.selectAll()

    def _handle_logout(self):
        """Xử lý đăng xuất."""
        reply = QMessageBox.question(
            self, "Xác nhận đăng xuất",
            f"Bạn có chắc muốn đăng xuất khỏi tài khoản {self.session.username}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self, "Đăng xuất",
                "Đã đăng xuất thành công. Ứng dụng sẽ đóng."
            )
            QApplication.quit()

    def _show_about(self):
        """Hiện dialog giới thiệu."""
        QMessageBox.about(
            self, "Giới thiệu",
            "<h2>💊 Tra Cứu Giá Thuốc</h2>"
            "<p><b>Phiên bản:</b> 2.0.0</p>"
            "<p>Phần mềm tra cứu giá thuốc trúng thầu từ kết quả đấu thầu.</p>"
            "<p>Hỗ trợ 2 nguồn dữ liệu:</p>"
            "<ul>"
            "<li><b>Mua sắm công:</b> Thuốc Generic, Biệt dược gốc, "
            "Thuốc Dược liệu, Dược liệu, Vị thuốc</li>"
            "<li><b>Bảo hiểm xã hội:</b> Dữ liệu BHXH</li>"
            "</ul>"
            "<p>Dữ liệu được đồng bộ từ Supabase và lưu trữ SQLite.</p>"
            "<hr>"
            "<p><i>Python + PyQt6 + SQLite + Supabase</i></p>"
        )

    def _show_user_manager(self):
        """Mở dialog quản lý tài khoản (Admin)."""
        from admin.user_manager import UserManagerDialog
        dialog = UserManagerDialog(self)
        dialog.exec()

    def _show_data_uploader(self):
        """Mở dialog đẩy dữ liệu (Admin)."""
        from admin.data_uploader import DataUploaderDialog
        dialog = DataUploaderDialog(self.db, self)
        dialog.exec()
