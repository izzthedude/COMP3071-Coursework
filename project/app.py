from PySide6.QtWidgets import *

from project.controller_app import AppController
from project.window_main import MainWindow


class App(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setApplicationName("Navigator")
        self.setApplicationDisplayName("Navigator")
        self.setApplicationVersion("0.1.0")

        self.main_window = MainWindow()
        self.main_window.quit_shortcut.activated.connect(self._on_quit_shortcut)

        self.app_controller = AppController(self.main_window)

        self.main_window.show()

    def _on_quit_shortcut(self):
        self.quit()
