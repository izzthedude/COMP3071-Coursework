from PySide6.QtWidgets import *

from project.environment import Environment
from project.ui.controller import AppController
from project.ui.window import MainWindow


class App(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setApplicationName("Navigator")
        self.setApplicationDisplayName("Navigator")
        self.setApplicationVersion("0.1.0")

        self.environment = Environment()

        self.main_window = MainWindow()
        self.main_window.quit_shortcut.activated.connect(self._on_quit_shortcut)

        self.app_controller = AppController(self.environment, self.main_window)

        self.main_window.show()

    def _on_quit_shortcut(self):
        self.quit()
