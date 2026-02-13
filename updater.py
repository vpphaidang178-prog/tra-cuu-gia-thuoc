
import os
import sys
import webbrowser
import requests
from PyQt6.QtWidgets import QMessageBox
from version import VERSION
from supabase_manager import SupabaseDataManager  # Assuming you have a SupabaseManager

class AppUpdater:
    def __init__(self, parent=None):
        self.parent = parent
        self.supabase = SupabaseDataManager() # Or get the client differently
        # URL of the version.json file in Supabase Storage
        # You need to replace this with your actual public URL
        self.version_url = f"{self.supabase.supabase_url}/storage/v1/object/public/releases/version.json"

    def check_for_updates(self, manual=False):
        try:
            response = requests.get(self.version_url, timeout=5)
            if response.status_code == 200:
                remote_info = response.json()
                remote_version = remote_info.get("version")
                download_url = remote_info.get("url")
                
                if self._is_newer(remote_version):
                    self._show_update_dialog(remote_version, download_url)
                elif manual:
                    QMessageBox.information(self.parent, "Cập nhật", "Bạn đang sử dụng phiên bản mới nhất.")
            else:
                if manual:
                     QMessageBox.warning(self.parent, "Lỗi", "Không thể kiểm tra cập nhật.")
        except Exception as e:
            print(f"Error checking for updates: {e}")
            if manual:
                QMessageBox.warning(self.parent, "Lỗi", f"Lỗi khi kiểm tra cập nhật: {e}")

    def _is_newer(self, remote_version):
        if not remote_version:
            return False
            
        def parse_version(v):
            return [int(x) for x in v.split('.')]

        try:
            return parse_version(remote_version) > parse_version(VERSION)
        except ValueError:
            return False

    def _show_update_dialog(self, version, url):
        msg = QMessageBox(self.parent)
        msg.setWindowTitle("Cập nhật mới")
        msg.setText(f"Đã có phiên bản mới: {version}")
        msg.setInformativeText("Bạn có muốn tải xuống ngay bây giờ không?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            webbrowser.open(url)
