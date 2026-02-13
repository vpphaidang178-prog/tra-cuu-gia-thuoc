"""
Login Dialog - Đăng nhập bằng username/password
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QApplication, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from auth.supabase_client import SupabaseAuth
from auth.session import Session
from theme_manager import ThemeManager


class LoginDialog(QDialog):
    """Dialog đăng nhập bằng username/password."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth = SupabaseAuth()
        self.session: Session = Session()
        self.theme_manager = ThemeManager()
        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        self.setWindowTitle("Tra Cuu Gia Thuoc - Dang nhap")
        self.setFixedSize(480, 540)
        self.setModal(True)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint
        )

        # Center on screen
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(
                (geo.width() - self.width()) // 2,
                (geo.height() - self.height()) // 2,
            )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== BANNER =====
        banner = QFrame()
        banner.setFixedHeight(130)
        banner.setObjectName("banner")
        banner_layout = QVBoxLayout(banner)
        banner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        banner_layout.setSpacing(6)

        icon_label = QLabel("\U0001f48a")
        icon_label.setFont(QFont("Segoe UI Emoji", 32))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")
        banner_layout.addWidget(icon_label)

        app_name = QLabel("TRA CUU GIA THUOC")
        app_name.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet(
            "color: #ffffff; background: transparent; letter-spacing: 2px;"
        )
        banner_layout.addWidget(app_name)

        main_layout.addWidget(banner)

        # ===== CARD =====
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(44, 28, 44, 24)
        card_layout.setSpacing(0)

        welcome = QLabel("Dang nhap he thong")
        welcome.setObjectName("welcomeLabel")
        welcome.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(welcome)

        card_layout.addSpacing(4)

        desc = QLabel("Nhap tai khoan duoc admin cap de tiep tuc")
        desc.setObjectName("descLabel")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(desc)

        card_layout.addSpacing(24)

        # --- Username field ---
        user_label = QLabel("TAI KHOAN")
        user_label.setObjectName("fieldLabel")
        card_layout.addWidget(user_label)
        card_layout.addSpacing(5)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhap ten tai khoan...")
        self.username_input.setObjectName("inputField")
        self.username_input.setMinimumHeight(44)
        card_layout.addWidget(self.username_input)

        card_layout.addSpacing(16)

        # --- Password field ---
        pw_label = QLabel("MAT KHAU")
        pw_label.setObjectName("fieldLabel")
        card_layout.addWidget(pw_label)
        card_layout.addSpacing(5)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Nhap mat khau...")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setObjectName("inputField")
        self.password_input.setMinimumHeight(44)
        self.password_input.returnPressed.connect(self._handle_login)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(24)

        # --- Login button ---
        self.login_btn = QPushButton("DANG NHAP")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setMinimumHeight(46)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self._handle_login)
        card_layout.addWidget(self.login_btn)

        card_layout.addSpacing(10)

        # --- Cancel ---
        cancel_btn = QPushButton("Huy")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setMinimumHeight(38)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        card_layout.addWidget(cancel_btn)

        card_layout.addSpacing(14)

        # --- Error label ---
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        card_layout.addWidget(self.error_label)

        main_layout.addWidget(card, 1)

        # ===== FOOTER =====
        footer = QLabel("Phien ban 2.0.0")
        footer.setObjectName("footerLabel")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setFixedHeight(32)
        main_layout.addWidget(footer)

    def _apply_styles(self):
        theme = self.theme_manager.get_theme()
        self.setStyleSheet(f"""
            QDialog {{ background-color: {theme['app_bg']}; }}

            #banner {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {theme['primary']}, stop:0.5 {theme['accent']}, stop:1 {theme['primary_pressed']}
                );
                border: none;
            }}

            #card {{
                background-color: {theme['widget_bg']};
                border: 1px solid {theme['border']};
            }}

            #welcomeLabel {{
                color: {theme['text_main']};
                background: transparent;
            }}

            #descLabel {{
                color: {theme['text_dim']};
                font-size: 12px;
                background: transparent;
            }}

            #fieldLabel {{
                color: {theme['text_dim']};
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1.5px;
                background: transparent;
            }}

            #inputField {{
                background-color: {theme['input_bg']};
                color: {theme['text_main']};
                border: 1.5px solid {theme['border']};
                border-radius: 10px;
                padding: 10px 14px;
                font-size: 14px;
                font-family: "Segoe UI";
            }}
            #inputField:focus {{
                border: 1.5px solid {theme['primary']};
            }}
            #inputField::placeholder {{ color: {theme['input_placeholder']}; }}

            #loginBtn {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme['primary']}, stop:1 {theme['accent']}
                );
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 1.5px;
                font-family: "Segoe UI";
            }}
            #loginBtn:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme['primary_hover']}, stop:1 {theme['primary']}
                );
            }}
            #loginBtn:pressed {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme['primary_pressed']}, stop:1 {theme['primary_pressed']}
                );
            }}
            #loginBtn:disabled {{
                background: {theme['border']}; color: {theme['text_dim']};
            }}

            #cancelBtn {{
                background-color: transparent;
                color: {theme['text_dim']};
                border: 1.5px solid {theme['border']};
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                font-family: "Segoe UI";
            }}
            #cancelBtn:hover {{
                background-color: {theme['app_bg']};
                color: {theme['text_main']};
                border-color: {theme['text_dim']};
            }}

            #errorLabel {{
                color: #f85149;
                background-color: rgba(248, 81, 73, 0.1);
                border: 1px solid rgba(248, 81, 73, 0.3);
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                font-weight: 600;
            }}

            #footerLabel {{
                color: {theme['text_dim']};
                font-size: 11px;
                background-color: {theme['app_bg']};
                border-top: 1px solid {theme['border']};
            }}
        """)

    def _handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self._show_error("Vui long nhap day du tai khoan va mat khau!")
            return

        self.error_label.setVisible(False)
        self.login_btn.setEnabled(False)
        self.login_btn.setText("DANG XU LY...")
        QApplication.processEvents()

        success, message, user_data = self.auth.login(username, password)

        self.login_btn.setEnabled(True)
        self.login_btn.setText("DANG NHAP")

        if success:
            self.session = Session(user_data)
            self.accept()
        else:
            self._show_error(message)
            self.password_input.clear()
            self.password_input.setFocus()

    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def get_session(self) -> Session:
        return self.session
