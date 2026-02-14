
import os
import sys
import webbrowser
import requests
import subprocess
import tempfile
from PyQt6.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import QObject, pyqtSignal, QThread, Qt
from version import VERSION
from supabase_manager import SupabaseDataManager

class UpdateWorker(QThread):
    finished = pyqtSignal(dict) # result dict

    def __init__(self, version_url):
        super().__init__()
        self.version_url = version_url

    def run(self):
        try:
            response = requests.get(self.version_url, timeout=5)
            if response.status_code == 200:
                self.finished.emit({"success": True, "data": response.json()})
            else:
                self.finished.emit({"success": False, "error": f"Status code: {response.status_code}"})
        except Exception as e:
            self.finished.emit({"success": False, "error": str(e)})

class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str) # success, file_path_or_error

    def __init__(self, url, dest_path):
        super().__init__()
        self.url = url
        self.dest_path = dest_path
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            response = requests.get(self.url, stream=True, timeout=10)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(self.dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self._is_cancelled:
                        self.finished.emit(False, "Đã hủy tải xuống.")
                        return
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            percent = int((downloaded_size / total_size) * 100)
                            self.progress.emit(percent)
            
            self.finished.emit(True, self.dest_path)
            
        except Exception as e:
            self.finished.emit(False, str(e))

class UpdateProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Đang tải cập nhật")
        self.setFixedSize(400, 150)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint) # Remove close button

        layout = QVBoxLayout(self)

        self.lbl_status = QLabel("Đang tải xuống bộ cài đặt...")
        layout.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def update_progress(self, percent):
        self.progress_bar.setValue(percent)
        self.lbl_status.setText(f"Đang tải: {percent}%")

class AppUpdater(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.supabase = SupabaseDataManager() 
        self.version_url = f"{self.supabase.supabase_url}/storage/v1/object/public/releases/version.json"
        self.manual_check = False
        self.download_worker = None
        self.progress_dialog = None

    def check_for_updates(self, manual=False):
        self.manual_check = manual
        self.worker = UpdateWorker(self.version_url)
        self.worker.finished.connect(self._on_check_finished)
        self.worker.start()

    def _on_check_finished(self, result):
        if result["success"]:
            remote_info = result["data"]
            remote_version = remote_info.get("version")
            download_url = remote_info.get("url")
            
            if self._is_newer(remote_version):
                self._offer_update(remote_version, download_url)
            elif self.manual_check:
                QMessageBox.information(self.parent, "Cập nhật", "Bạn đang sử dụng phiên bản mới nhất.")
        else:
            if self.manual_check:
                QMessageBox.warning(self.parent, "Lỗi", f"Không thể kiểm tra cập nhật: {result.get('error')}")

    def _is_newer(self, remote_version):
        if not remote_version:
            return False
            
        def parse_version(v):
            return [int(x) for x in v.split('.')]

        try:
            return parse_version(remote_version) > parse_version(VERSION)
        except ValueError:
            return False

    def _offer_update(self, version, url):
        msg = QMessageBox(self.parent)
        msg.setWindowTitle("Cập nhật mới")
        msg.setText(f"Đã có phiên bản mới: {version}")
        msg.setInformativeText("Bạn có muốn cập nhật ngay bây giờ không?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        msg.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self._start_download(url)

    def _start_download(self, url: str):
        # Temp file
        temp_dir = tempfile.gettempdir()
        filename = "setup_tracuugiathuoc_update.exe"
        self.dest_path = os.path.join(temp_dir, filename)

        # Show Progress Dialog
        self.progress_dialog = UpdateProgressDialog(self.parent)
        
        # Start Worker
        self.download_worker = DownloadWorker(url, self.dest_path)
        if self.progress_dialog:
            self.download_worker.progress.connect(self.progress_dialog.update_progress)
            self.progress_dialog.rejected.connect(self.download_worker.cancel)
        
        self.download_worker.finished.connect(self._on_download_finished)
        
        self.download_worker.start()
        if self.progress_dialog:
            self.progress_dialog.exec()

    def _on_download_finished(self, success: bool, message: str):
        if self.progress_dialog:
            self.progress_dialog.close()
            
        if success:
            # message is file_path
            self._install_update(message)
        else:
            if message != "Đã hủy tải xuống.":
                QMessageBox.warning(self.parent, "Lỗi tải xuống", f"Không thể tải bản cập nhật:\n{message}")

    def _install_update(self, file_path: str):
        try:
            # Launch installer
            subprocess.Popen([file_path], shell=True)
            # Quit app
            sys.exit(0)
        except Exception as e:
            QMessageBox.critical(self.parent, "Lỗi", f"Không thể chạy file cài đặt: {e}")
