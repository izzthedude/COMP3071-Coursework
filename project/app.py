from PySide6.QtWidgets import *

from project.window_main import MainWindow
from project.controller_app import AppController


class App(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setApplicationName("Navigator")

        self.main_window = MainWindow()
        self.main_window.quit_shortcut.activated.connect(self._on_quit_shortcut)

        self.app_controller = AppController(self.main_window)

        self.main_window.show()

    def _on_quit_shortcut(self):
        self.quit()
