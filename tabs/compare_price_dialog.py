"""
Dialog: Đối chiếu giá trúng thầu.
Gồm 5 tab: Generic, Biệt dược gốc, Dược liệu, Dược liệu (Raw), Vị thuốc.
Chức năng: Tải file mẫu, Import Excel, Đối chiếu tự động/thủ công.
"""

import pandas as pd
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QProgressBar, QLabel, QFrame,
    QInputDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from database import DatabaseManager, TABLE_SCHEMAS
from tabs.search_selection_dialog import SearchSelectionDialog

# Helper to normalize price
def format_currency(value):
    try:
        if isinstance(value, str):
            value = int("".join(filter(str.isdigit, value)))
        return f"{value:,.0f}" if value else "0"
    except:
        return "0"

class AutoCompareWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    row_updated = pyqtSignal(int, dict) # row_index, stats dict

    def __init__(self, db, table_name, rows_data, criteria_cols):
        super().__init__()
        self.db = db
        self.table_name = table_name
        self.rows_data = rows_data # List of dicts or objects
        self.criteria_cols = criteria_cols # Mapping: {db_col: index_in_row}

    def run(self):
        total = len(self.rows_data)
        for i, row in enumerate(self.rows_data):
            criteria = {}
            for db_col, row_idx in self.criteria_cols.items():
                val = row[row_idx]
                if val:
                    criteria[db_col] = val
            
            # Additional logic for 'Nhom thuoc' matching if user requested
            # User req: Tên hoạt chất, Nồng độ/Hàm lượng, Dạng bào chế, Nhóm thuốc (Nhóm TCKT)
            # criteria dictionary should match what get_price_statistics expects
            
            stats = self.db.get_price_statistics(self.table_name, criteria)
            self.row_updated.emit(i, stats)
            self.progress.emit(int((i + 1) / total * 100))
        
        self.finished.emit()


class CompareTab(QWidget):
    def __init__(self, db: DatabaseManager, table_name: str, parent=None):
        super().__init__(parent)
        self.db = db
        self.table_name = table_name
        
        # Define Columns based on User Request
        # Tab 1-4 share similar structure, Tab 5 (Vi thuoc) differs slightly
        
        base_cols = [
            "STT", "STT Thông tư", "Mã thuốc", "Tên hoạt chất",
            "Nồng độ/Hàm lượng", "Dạng bào chế", "Dạng trình bày",
            "Đường dùng", "Đơn vị tính", "Nhóm TCKT",
            "Đơn giá tham khảo", "Giá Min", "Giá Max", "Số kết quả tìm thấy"
        ]
        
        # Adjust for Tab 2 (Biệt dược gốc) - "Tên thuốc" added
        if table_name == "thuoc_biet_duoc":
            base_cols.insert(3, "Tên thuốc")
            
        # Adjust for Tab 5 (Vi thuoc)
        if table_name == "vi_thuoc":
            base_cols = [
                "STT", "STT Thông tư", "Mã thuốc", "Tên vị thuốc",
                "Tên khoa học", "Bộ phận dùng", "Phương pháp chế biến",
                "Tiêu chuẩn chất lượng", "Đơn vị tính", "Nhóm TCKT",
                "Đơn giá tham khảo", "Giá Min", "Giá Max", "Số kết quả tìm thấy"
            ]
        
        self.columns = base_cols
        
        # Mappings for Auto Compare criteria: DB Col Name -> Table Column Index
        # Indices need to be calculated dynamically based on self.columns
        self.criteria_mapping = {}
        
        # Standardize criteria mapping
        def get_idx(name):
            try:
                return self.columns.index(name)
            except ValueError:
                return -1

        if table_name in ["thuoc_generic", "thuoc_biet_duoc", "thuoc_duoc_lieu"]:
            # DB: ten_hoat_chat, nong_do_ham_luong, dang_bao_che, nhom_thuoc
            # Table: Tên hoạt chất, Nồng độ/Hàm lượng, Dạng bào chế, Nhóm TCKT
            self.criteria_mapping = {
                'ten_hoat_chat': get_idx("Tên hoạt chất"),
                'nong_do_ham_luong': get_idx("Nồng độ/Hàm lượng"),
                'dang_bao_che': get_idx("Dạng bào chế"),
                'nhom_thuoc': get_idx("Nhóm TCKT")
            }
        elif table_name == "duoc_lieu": # Raw Herbal
            # DB: ten_duoc_lieu (mapped from Tên hoạt chất for UI consistency?), ...
            # Actually user said "Tab 4 Bảng Dược liệu" cols allow "Tên hoạt chất".
            # Assuming "Tên hoạt chất" in Excel maps to "ten_duoc_lieu" in DB for raw herbal?
            # Or is it "Tên dược liệu"?
            # Let's assume input "Tên hoạt chất" -> DB "ten_duoc_lieu"
            self.criteria_mapping = {
                'ten_duoc_lieu': get_idx("Tên hoạt chất"), # User calls it Tên hoạt chất in UI req
                'nong_do_ham_luong': get_idx("Nồng độ/Hàm lượng"),
                 # Check specific cols for duoc_lieu in database.py if needed.
                 # duoc_lieu schema: ten_duoc_lieu, bo_phan_dung, ten_khoa_hoc...
                 # It doesn't have 'nong_do_ham_luong' or 'dang_bao_che' in standard schema?
                 # Wait, user req for Tab 4 has "Nồng độ", "Dạng bào chế".
                 # If DB schema doesn't match, auto compare might fail or needs lenient mapping.
                 # Re-checking database.py...
                 # duoc_lieu schema: ten_duoc_lieu, bo_phan_dung, ten_khoa_hoc, nguon_goc...
                 # It does NOT have nong_do_ham_luong, dang_bao_che.
                 # User request might be copying Generic structure.
                 # For Tab 4, I will only map 'ten_duoc_lieu' and maybe 'nhom_tckt'.
                 'nhom_tckt': get_idx("Nhóm TCKT")
            }
        elif table_name == "vi_thuoc":
            # DB: ten_vi_thuoc, ten_khoa_hoc, bo_phan_dung
            self.criteria_mapping = {
                'ten_vi_thuoc': get_idx("Tên vị thuốc"),
                'ten_khoa_hoc': get_idx("Tên khoa học"),
                'bo_phan_dung': get_idx("Bộ phận dùng"),
                'nhom_tckt': get_idx("Nhóm TCKT")
            }

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Actions
        btn_layout = QHBoxLayout()
        self.btn_template = QPushButton("⬇ Tải file mẫu")
        self.btn_template.clicked.connect(self._download_template)
        btn_layout.addWidget(self.btn_template)
        
        self.btn_import = QPushButton("📥 Nạp dữ liệu (Excel)")
        self.btn_import.clicked.connect(self._import_excel)
        btn_layout.addWidget(self.btn_import)
        
        self.btn_compare = QPushButton("⚡ Đối chiếu Tự động")
        self.btn_compare.clicked.connect(self._auto_compare)
        btn_layout.addWidget(self.btn_compare)
        
        
        self.btn_export = QPushButton("📤 Xuất Excel")
        self.btn_export.clicked.connect(self._export_excel)
        btn_layout.addWidget(self.btn_export)

        self.btn_save_draft = QPushButton("💾 Lưu Nháp")
        self.btn_save_draft.clicked.connect(self._save_draft)
        btn_layout.addWidget(self.btn_save_draft)

        self.btn_load_draft = QPushButton("📂 Tải Nháp")
        self.btn_load_draft.clicked.connect(self._load_draft)
        btn_layout.addWidget(self.btn_load_draft)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.setAlternatingRowColors(True)
        # Double click to manual compare
        self.table.doubleClicked.connect(self._manual_compare)
        
        layout.addWidget(self.table)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Status Label
        self.lbl_status = QLabel("Double click vào dòng để đối chiếu thủ công.")
        self.lbl_status.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.lbl_status)

    def _download_template(self):
        path, _ = QFileDialog.getSaveFileName(self, "Lưu file mẫu", f"Mau_{self.table_name}.xlsx", "Excel Files (*.xlsx)")
        if path:
            df = pd.DataFrame(columns=self.columns)
            df.to_excel(path, index=False)
            QMessageBox.information(self, "Thành công", "Đã tạo file mẫu thành công.")

    def _import_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Chọn file Excel", "", "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)")
        if path:
            try:
                df = pd.read_excel(path) if not path.endswith('.csv') else pd.read_csv(path)
                df = df.fillna("")
                
                # Check columns match roughly? Or just map by index/name?
                # Prepare to load into table
                # We expect user to use the template, so columns should match.
                # If they don't, we try to match by name, else error.
                
                self.table.setRowCount(0)
                self.table.setRowCount(len(df))
                
                # Map DF columns to Table Columns
                header_map = {}
                for col in df.columns:
                    if col in self.columns:
                        header_map[col] = self.columns.index(col)
                
                for r in range(len(df)):
                    row = df.iloc[r]
                    for col_name in df.columns:
                        if col_name in header_map:
                            c = header_map[col_name]
                            val = str(row[col_name])
                            self.table.setItem(r, c, QTableWidgetItem(val))
                            
                QMessageBox.information(self, "Thành công", f"Đã nạp {len(df)} dòng dữ liệu.")
                
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể đọc file: {str(e)}")

    def _auto_compare(self):
        if self.table.rowCount() == 0:
            return

        # 1. Ask user for Target Table
        # Default to current table type
        items = [
            "Thuốc Generic", "Thuốc Biệt dược gốc", 
            "Thuốc Dược liệu", "Dược liệu", 
            "Vị thuốc", "Bảo hiểm xã hội"
        ]
        
        # Map Display Name -> Table Name
        name_map = {
            "Thuốc Generic": "thuoc_generic",
            "Thuốc Biệt dược gốc": "thuoc_biet_duoc",
            "Thuốc Dược liệu": "thuoc_duoc_lieu",
            "Dược liệu": "duoc_lieu",
            "Vị thuốc": "vi_thuoc",
            "Bảo hiểm xã hội": "bhxh"
        }
        
        # Determine current name based on self.table_name
        current_idx = 0
        for name, code in name_map.items():
            if code == self.table_name:
                current_idx = items.index(name)
                break
        
        item, ok = QInputDialog.getItem(self, "Chọn bảng đối chiếu", 
                                        "Chọn bảng dữ liệu đích để đối chiếu:", 
                                        items, current_idx, False)
        
        if not ok or not item:
            return
            
        target_table = name_map[item]
        
        # 2. Generate Criteria Mapping dynamically
        criteria_mapping = self._get_criteria_mapping_for_target(target_table)
        
        if not criteria_mapping:
            QMessageBox.warning(self, "Cảnh báo", f"Không tìm thấy cột phù hợp để đối chiếu với bảng '{item}'.")
            return
            
        self.btn_compare.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        # Prepare data for thread
        rows_data = []
        for r in range(self.table.rowCount()):
            row_items = []
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                row_items.append(item.text() if item else "")
            rows_data.append(row_items)
            
        self.worker = AutoCompareWorker(self.db, target_table, rows_data, criteria_mapping)
        self.worker.row_updated.connect(self._update_row_stats)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self._on_compare_finished)
        self.worker.start()

    def _get_criteria_mapping_for_target(self, target_table):
        """Builds criteria {'db_col': excel_col_idx} based on target table type."""
        
        def get_idx(name):
            try:
                return self.columns.index(name)
            except ValueError:
                # Try partial match or aliases?
                # For now strict match on common names
                # Fallback aliases
                aliases = {
                    "Tên hoạt chất": ["Tên dược liệu", "Tên vị thuốc", "Hoạt chất"],
                    "Tên dược liệu": ["Tên hoạt chất"],
                    "Tên vị thuốc": ["Tên hoạt chất"],
                    "Nồng độ/Hàm lượng": ["Hàm lượng", "Nồng độ"],
                    "Nhóm TCKT": ["Nhóm thuốc"]
                }
                
                if name in aliases:
                    for alias in aliases[name]:
                        if alias in self.columns:
                            return self.columns.index(alias)
                return -1

        mapping = {}
        
        if target_table in ["thuoc_generic", "thuoc_biet_duoc", "thuoc_duoc_lieu"]:
            # Standard Drug Schema
            # Needs: ten_hoat_chat, nong_do_ham_luong, dang_bao_che, nhom_thuoc
            idx_name = get_idx("Tên hoạt chất")
            if idx_name != -1: mapping['ten_hoat_chat'] = idx_name
            
            idx_content = get_idx("Nồng độ/Hàm lượng")
            if idx_content != -1: mapping['nong_do_ham_luong'] = idx_content
            
            idx_form = get_idx("Dạng bào chế")
            if idx_form != -1: mapping['dang_bao_che'] = idx_form
            
            idx_group = get_idx("Nhóm TCKT")
            if idx_group != -1: mapping['nhom_thuoc'] = idx_group

        elif target_table == "duoc_lieu":
            # Raw Herbal
            # Needs: ten_duoc_lieu, nhom_tckt
            idx_name = get_idx("Tên hoạt chất") # Treating Active Ingredient as Material Name
            if idx_name == -1: idx_name = get_idx("Tên dược liệu")
            
            if idx_name != -1: mapping['ten_duoc_lieu'] = idx_name
            
            idx_group = get_idx("Nhóm TCKT")
            if idx_group != -1: mapping['nhom_tckt'] = idx_group
            
        elif target_table == "vi_thuoc":
            # Traditional
            # Needs: ten_vi_thuoc, ten_khoa_hoc, bo_phan_dung, nhom_tckt
            idx_name = get_idx("Tên vị thuốc")
            if idx_name == -1: idx_name = get_idx("Tên hoạt chất")
            
            if idx_name != -1: mapping['ten_vi_thuoc'] = idx_name
            
            idx_sci = get_idx("Tên khoa học")
            if idx_sci != -1: mapping['ten_khoa_hoc'] = idx_sci
            
            idx_part = get_idx("Bộ phận dùng")
            if idx_part != -1: mapping['bo_phan_dung'] = idx_part
            
            idx_group = get_idx("Nhóm TCKT")
            if idx_group != -1: mapping['nhom_tckt'] = idx_group

        elif target_table == "bhxh":
            # BHXH Schema
            # Needs: hoat_chat, ham_luong, dang_bao_che, nhom_tckt
            # Note: bhxh uses 'hoat_chat' not 'ten_hoat_chat'
            idx_name = get_idx("Tên hoạt chất")
            if idx_name != -1: mapping['hoat_chat'] = idx_name
            
            idx_content = get_idx("Nồng độ/Hàm lượng")
            if idx_content != -1: mapping['ham_luong'] = idx_content
            
            idx_form = get_idx("Dạng bào chế")
            if idx_form != -1: mapping['dang_bao_che'] = idx_form
            
            idx_group = get_idx("Nhóm TCKT")
            if idx_group != -1: mapping['nhom_tckt'] = idx_group
            
        return mapping

    def _update_row_stats(self, row_idx, stats):
        # Update Min, Max, Count, Ref Price (if needed)
        # Stats: min, max, count
        # Columns: "Đơn giá tham khảo", "Giá Min", "Giá Max", "Số kết quả tìm thấy"
        # Indices:
        try:
             idx_min = self.columns.index("Giá Min")
             idx_max = self.columns.index("Giá Max")
             idx_count = self.columns.index("Số kết quả tìm thấy")
             # idx_ref = self.columns.index("Đơn giá tham khảo") # Optional to update?
             
             self.table.setItem(row_idx, idx_min, QTableWidgetItem(format_currency(stats['min'])))
             self.table.setItem(row_idx, idx_max, QTableWidgetItem(format_currency(stats['max'])))
             self.table.setItem(row_idx, idx_count, QTableWidgetItem(str(stats['count'])))
             
        except ValueError:
            pass

    def _on_compare_finished(self):
        self.progress.setVisible(False)
        self.btn_compare.setEnabled(True)
        QMessageBox.information(self, "Hoàn tất", "Đã hoàn thành đối chiếu tự động.")

    def _manual_compare(self, index):
        row = index.row()
        
        # 1. Ask user for Target Table (Same as Auto Compare)
        items = [
            "Thuốc Generic", "Thuốc Biệt dược gốc", 
            "Thuốc Dược liệu", "Dược liệu", 
            "Vị thuốc", "Bảo hiểm xã hội"
        ]
        
        name_map = {
            "Thuốc Generic": "thuoc_generic",
            "Thuốc Biệt dược gốc": "thuoc_biet_duoc",
            "Thuốc Dược liệu": "thuoc_duoc_lieu",
            "Dược liệu": "duoc_lieu",
            "Vị thuốc": "vi_thuoc",
            "Bảo hiểm xã hội": "bhxh"
        }
        
        # Default to current table type
        current_idx = 0
        for name, code in name_map.items():
            if code == self.table_name:
                current_idx = items.index(name)
                break
        
        item, ok = QInputDialog.getItem(self, "Chọn bảng đối chiếu", 
                                        "Chọn bảng dữ liệu đích để tìm kiếm:", 
                                        items, current_idx, False)
        
        if not ok or not item:
            return
            
        target_table = name_map[item]

        # Initial keyword from "Tên hoạt chất" or similar
        keyword = ""
        possible_cols = ["Tên hoạt chất", "Tên thuốc", "Tên dược liệu", "Tên vị thuốc", "Hoạt chất"]
        for col in possible_cols:
            if col in self.columns:
                try:
                    c_idx = self.columns.index(col)
                    item_cell = self.table.item(row, c_idx)
                    if item_cell:
                        keyword = item_cell.text()
                    break
                except ValueError:
                    continue
        
        # Open Dialog with TARGET table
        dialog = SearchSelectionDialog(self.db, target_table, keyword, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_data:
            # selected_data is a tuple from DB (id, col1, col2...)
            sel_price = 0
            
            # Find price in selected_data based on TARGET table schema
            schema = TABLE_SCHEMAS.get(target_table, [])
            
            # Use 'gia' for BHXH, 'don_gia' for others, or 'don_gia_trung_thau'
            # Check schema cols
            col_names = [c[0] for c in schema]
            
            price_col = 'don_gia' # default
            if 'don_gia_trung_thau' in col_names:
                price_col = 'don_gia_trung_thau'
            elif 'gia' in col_names:
                price_col = 'gia'
                
            price_idx = -1
            # Find index in schema
            for i, col_name in enumerate(col_names):
                if col_name == price_col:
                    price_idx = i + 1 # +1 for ID
                    break
            
            if price_idx != -1 and price_idx < len(dialog.selected_data):
                raw_price = dialog.selected_data[price_idx]
                if isinstance(raw_price, str):
                    # Clean price string
                    sel_price = int("".join(filter(str.isdigit, raw_price))) if raw_price else 0
                elif isinstance(raw_price, (int, float)):
                    sel_price = int(raw_price)

            # Update Table
            try:
                idx_ref = self.columns.index("Đơn giá tham khảo")
                self.table.setItem(row, idx_ref, QTableWidgetItem(format_currency(sel_price)))
                
                # Optional: Update other cols if single match implies these?
                # For manual, usually we just set the Ref Price.
                
            except ValueError:
                pass


    def _export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Xuất Excel", f"KetQua_{self.table_name}.xlsx", "Excel Files (*.xlsx)")
        if path:
            # Gather data
            headers = self.columns
            data = []
            for r in range(self.table.rowCount()):
                row_data = []
                for c in range(self.table.columnCount()):
                    item = self.table.item(r, c)
                    row_data.append(item.text() if item else "")
                data.append(row_data)
            
            df = pd.DataFrame(data, columns=headers)
            df.to_excel(path, index=False)
            QMessageBox.information(self, "Thành công", "Đã xuất file thành công.")

    def _get_draft_path(self):
        # Create drafts dir if not exists
        base_dir = os.path.dirname(os.path.abspath(__file__)) # tabs/
        root_dir = os.path.dirname(base_dir) # app root
        drafts_dir = os.path.join(root_dir, "user_data", "drafts")
        os.makedirs(drafts_dir, exist_ok=True)
        return os.path.join(drafts_dir, f"draft_{self.table_name}.json")

    def _save_draft(self):
        try:
            # Collect data
            data = []
            for r in range(self.table.rowCount()):
                row_data = {}
                for c in range(self.table.columnCount()):
                    header = self.columns[c]
                    item = self.table.item(r, c)
                    row_data[header] = item.text() if item else ""
                data.append(row_data)
            
            if not data:
                QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu để lưu.")
                return

            df = pd.DataFrame(data)
            path = self._get_draft_path()
            df.to_json(path, orient='records', force_ascii=False, indent=4)
            QMessageBox.information(self, "Thành công", f"Đã lưu bản nháp thành công.\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu bản nháp: {str(e)}")

    def _load_draft(self):
        path = self._get_draft_path()
        if not os.path.exists(path):
            QMessageBox.warning(self, "Thông báo", "Chưa có bản nháp nào được lưu cho bảng này.")
            return

        reply = QMessageBox.question(
            self, "Xác nhận", 
            "Tải bản nháp sẽ ghi đè dữ liệu hiện tại. Bạn có chắc chắn không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            df = pd.read_json(path, orient='records')
            df = df.fillna("")
            
            self.table.setRowCount(0)
            self.table.setRowCount(len(df))
            
            # Columns should match because it's saved from here
            # But handle case if columns changed in code?
            # Map by name
            header_map = {col: i for i, col in enumerate(self.columns)}
            
            for r in range(len(df)):
                row = df.iloc[r]
                for col_name, val in row.items():
                    if col_name in header_map:
                        c = header_map[col_name]
                        self.table.setItem(r, c, QTableWidgetItem(str(val)))
            
            QMessageBox.information(self, "Thành công", f"Đã tải {len(df)} dòng từ bản nháp.")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải bản nháp: {str(e)}")


class ComparePriceDialog(QDialog):
    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Kế hoạch LCNT - Đối chiếu giá trúng thầu")
        self.resize(1200, 800)
        
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        
        # Tab 1: Generic
        self.tab_generic = CompareTab(db, "thuoc_generic")
        self.tabs.addTab(self.tab_generic, "Thuốc Generic")
        
        # Tab 2: Brand
        self.tab_brand = CompareTab(db, "thuoc_biet_duoc")
        self.tabs.addTab(self.tab_brand, "Thuốc Biệt dược gốc")
        
        # Tab 3: Herbal
        self.tab_herbal = CompareTab(db, "thuoc_duoc_lieu")
        self.tabs.addTab(self.tab_herbal, "Thuốc Dược liệu")
        
        # Tab 4: Raw Herbal
        self.tab_raw = CompareTab(db, "duoc_lieu")
        self.tabs.addTab(self.tab_raw, "Dược liệu")
        
        # Tab 5: Traditional
        self.tab_trad = CompareTab(db, "vi_thuoc")
        self.tabs.addTab(self.tab_trad, "Vị thuốc")
        
        layout.addWidget(self.tabs)
