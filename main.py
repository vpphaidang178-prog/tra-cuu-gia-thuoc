"""
Tra Cứu Giá Thuốc - Desktop Application
Entry point

Chạy: python main.py
"""

import sys
import os

# Ensure the script's directory is in sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from auth.login_dialog import LoginDialog
from app import MainWindow


def main():
    # High DPI support
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    app = QApplication(sys.argv)

    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Set app metadata
    app.setApplicationName("Tra Cứu Giá Thuốc")
    app.setOrganizationName("DrugPriceLookup")
    app.setApplicationVersion("2.0.0")

    # Show login dialog first
    login_dialog = LoginDialog()
    if login_dialog.exec() != LoginDialog.DialogCode.Accepted:
        sys.exit(0)

    # Get session from login
    session = login_dialog.get_session()

    # Show main window with authenticated session
    window = MainWindow(session)
    window.show()

    # Check for updates silently on startup
    from updater import AppUpdater
    try:
        # AppUpdater now uses QThread internally, so we don't need threading.Thread here
        # We need to keep a reference to updater so it doesn't get garbage collected
        app.updater = AppUpdater() 
        app.updater.check_for_updates(manual=False)
    except Exception as e:
        print(f"Update check failed: {e}")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
