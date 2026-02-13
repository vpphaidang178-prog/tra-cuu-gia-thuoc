from PyQt6.QtCore import QObject, pyqtSignal
from themes import DARK_THEME, LIGHT_THEME

class ThemeManager(QObject):
    _instance = None
    theme_changed = pyqtSignal(dict)  # Signal emits the new theme dict

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._current_theme = DARK_THEME  # Default
        self._initialized = True

    def get_theme(self):
        return self._current_theme

    def toggle_theme(self):
        if self._current_theme["name"] == "Dark":
            self._current_theme = LIGHT_THEME
        else:
            self._current_theme = DARK_THEME
        
        self.theme_changed.emit(self._current_theme)

    @property
    def is_dark(self):
        return self._current_theme["name"] == "Dark"
