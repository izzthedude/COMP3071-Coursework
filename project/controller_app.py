from PySide6.QtCore import *

from project.window_main import MainWindow
from project.map_gen import MapGenerator


class AppController(QObject):
    def __init__(self, window: MainWindow, parent: QObject = None):
        super().__init__(parent)
        self._window: MainWindow = window

        self._map_size = 7
        self._generator = MapGenerator(self._map_size)
