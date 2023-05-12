import os

from PySide6.QtGui import *
from PySide6.QtWidgets import *

from project.environment import Environment
from project.ui.window import MainWindow


class App(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setApplicationName("Navigator")
        self.setApplicationDisplayName("Navigator")
        self.setApplicationVersion("0.1.0")
        self.setWindowIcon(QPixmap(os.path.join(os.path.dirname(__file__), "icon.svg")))

        self._environment = Environment()
        self._main_window = MainWindow(self._environment)
        self._main_window.quit_shortcut.activated.connect(self._on_quit_shortcut)
        self._main_window.show()

    def _on_quit_shortcut(self):
        self.quit()
