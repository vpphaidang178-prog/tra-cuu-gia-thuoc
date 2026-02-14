def get_stylesheet(theme):
    return f"""
/* ========== GLOBAL ========== */
QMainWindow {{
    background-color: {theme['app_bg']};
    color: {theme['text_main']};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}}

QWidget {{
    background-color: {theme['app_bg']};
    color: {theme['text_main']};
    font-family: "Segoe UI", Arial, sans-serif;
}}

/* ========== TABLE ========== */
QTableWidget {{
    background-color: {theme['widget_bg']};
    alternate-background-color: {theme['app_bg']};
    color: {theme['text_main']};
    gridline-color: {theme['grid_line']};
    border: 1px solid {theme['border']};
    border-radius: 6px;
    font-size: 12px;
    selection-background-color: {theme['selection_bg']};
    selection-color: {theme['selection_text']};
}}

QTableWidget::item {{
    padding: 6px 10px;
    border-bottom: 1px solid {theme['grid_line']};
}}

QTableWidget::item:selected {{
    background-color: {theme['selection_bg']};
    color: {theme['selection_text']};
}}

QTableWidget::item:hover {{
    background-color: {theme['primary']};
    color: #ffffff;
}}

QHeaderView::section {{
    background-color: {theme['primary']};
    color: #ffffff;
    padding: 8px 10px;
    border: none;
    border-right: 1px solid {theme['primary_hover']};
    border-bottom: 2px solid {theme['accent']};
    font-weight: 700;
    font-size: 12px;
}}

QHeaderView::section:hover {{
    background-color: {theme['primary_hover']};
}}

/* ========== SCROLLBAR ========== */
QScrollBar:vertical {{
    background-color: {theme['scrollbar_bg']};
    width: 12px;
    margin: 0;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {theme['scrollbar_handle']};
    min-height: 30px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {theme['primary_hover']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {theme['scrollbar_bg']};
    height: 12px;
    margin: 0;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {theme['scrollbar_handle']};
    min-width: 30px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {theme['primary_hover']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ========== LINE EDIT (Search) ========== */
QLineEdit {{
    background-color: {theme['input_bg']};
    color: {theme['text_main']};
    border: 2px solid {theme['border']};
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 14px;
    selection-background-color: {theme['accent']};
    selection-color: #ffffff;
}}

QLineEdit:focus {{
    border: 2px solid {theme['accent']};
    background-color: {theme['input_bg']};
}}

QLineEdit::placeholder {{
    color: {theme['input_placeholder']};
}}

/* ========== COMBO BOX ========== */
QComboBox {{
    background-color: {theme['input_bg']};
    color: {theme['text_main']};
    border: 2px solid {theme['border']};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    min-width: 150px;
}}

QComboBox:hover {{
    border: 2px solid {theme['primary_hover']};
}}

QComboBox:focus {{
    border: 2px solid {theme['accent']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {theme['accent']};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {theme['input_bg']};
    color: {theme['text_main']};
    border: 2px solid {theme['border']};
    selection-background-color: {theme['selection_bg']};
    selection-color: {theme['selection_text']};
    padding: 4px;
}}

/* ========== PUSH BUTTON ========== */
QPushButton {{
    background-color: {theme['primary']};
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {theme['primary_hover']};
}}

QPushButton:pressed {{
    background-color: {theme['primary_pressed']};
}}

QPushButton:disabled {{
    background-color: {theme['grid_line']};
    color: {theme['text_dim']};
}}

QPushButton#importBtn {{
    background-color: {theme['btn_import_bg']};
    font-weight: 700;
    padding: 10px 24px;
}}
QPushButton#importBtn:hover {{
    background-color: {theme['btn_import_hover']};
}}

QPushButton#clearBtn {{
    background-color: {theme['grid_line']};
    color: {theme['text_main']};
}}
QPushButton#clearBtn:hover {{
    background-color: {theme['scrollbar_handle']};
}}

QPushButton#exportBtn {{
    background-color: {theme['btn_export_bg']};
}}
QPushButton#exportBtn:hover {{
    background-color: {theme['btn_export_hover']};
}}

QPushButton#deleteDataBtn {{
    background-color: {theme['btn_delete_bg']};
}}
QPushButton#deleteDataBtn:hover {{
    background-color: {theme['btn_delete_hover']};
}}

QPushButton#syncBtn {{
    background-color: {theme['btn_sync_bg']};
    font-weight: 700;
}}
QPushButton#syncBtn:hover {{
    background-color: {theme['btn_sync_hover']};
}}

QPushButton#pushBtn {{
    background-color: {theme['btn_push_bg']};
    font-weight: 700;
}}
QPushButton#pushBtn:hover {{
    background-color: {theme['btn_push_hover']};
}}

/* ========== LABEL ========== */
QLabel {{
    color: {theme['text_main']};
    font-size: 13px;
}}

QLabel#titleLabel {{
    font-size: 16px;
    font-weight: 700;
    color: {theme['text_main']};
}}

QLabel#countLabel, QLabel#filterLabel {{
    font-size: 13px;
    color: {theme['text_dim']};
    font-weight: 500;
}}

QLabel#syncStatusLabel {{
    font-size: 12px;
    color: {theme['btn_sync_bg']};
    font-weight: 600;
}}

/* ========== STATUS BAR ========== */
QStatusBar {{
    background-color: {theme['primary']};
    color: #ffffff;
    border-top: 2px solid {theme['accent']};
    font-size: 12px;
    padding: 4px;
}}

/* ========== MENU BAR ========== */
QMenuBar {{
    background-color: {theme['primary']};
    color: #ffffff;
    font-size: 13px;
    padding: 2px;
}}

QMenuBar::item {{
    padding: 6px 14px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: {theme['primary_hover']};
}}

QMenu {{
    background-color: {theme['widget_bg']};
    color: {theme['text_main']};
    border: 1px solid {theme['border']};
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 30px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {theme['primary']};
    color: #ffffff;
}}

QMenu::separator {{
    height: 1px;
    background-color: {theme['grid_line']};
    margin: 4px 10px;
}}

/* ========== GROUP BOX ========== */
QGroupBox {{
    border: 1px solid {theme['border']};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
    color: {theme['text_dim']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
}}

/* ========== PROGRESS BAR ========== */
QProgressBar {{
    background-color: {theme['input_bg']};
    border: 1px solid {theme['border']};
    border-radius: 6px;
    text-align: center;
    color: {theme['text_main']};
    font-size: 11px;
    height: 20px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {theme['primary']}, stop:1 {theme['accent']});
    border-radius: 5px;
}}

/* ========== DIALOG ========== */
QDialog {{
    background-color: {theme['app_bg']};
    color: {theme['text_main']};
}}

/* ========== MESSAGE BOX ========== */
QMessageBox {{
    background-color: {theme['app_bg']};
}}

QMessageBox QLabel {{
    color: {theme['text_main']};
    font-size: 13px;
}}

/* ========== TAB WIDGET ========== */
QTabWidget::pane {{
    border: 1px solid {theme['border']};
    background-color: {theme['widget_bg']};
}}

QTabWidget::tab-bar {{
    left: 5px; /* move to the right by 5px */
}}

QTabBar::tab {{
    background-color: {theme['app_bg']};
    color: {theme['text_dim']};
    border: 1px solid {theme['border']};
    border-bottom-color: {theme['border']};
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 4px;
}}

QTabBar::tab:selected {{
    background-color: {theme['widget_bg']};
    color: {theme['primary']};
    font-weight: 700;
    border-bottom: 2px solid {theme['primary']};
}}

QTabBar::tab:hover:!selected {{
    background-color: {theme['grid_line']};
    color: {theme['text_main']};
}}

/* ========== STACKED WIDGET ========== */
QStackedWidget {{
    background-color: {theme['app_bg']};
}}
"""
