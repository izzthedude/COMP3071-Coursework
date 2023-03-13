from PySide6.QtGui import *
from PySide6.QtWidgets import *

from project.ui.window_main import MainWindow


class App(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setApplicationName("Navigator")

        self.main_window = MainWindow()
        self.main_window.quit_shortcut.activated.connect(self._on_quit_shortcut)

        self.main_window.show()

    def _on_quit_shortcut(self):
        self.quit()
