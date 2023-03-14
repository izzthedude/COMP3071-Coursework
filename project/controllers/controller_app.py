from PySide6.QtCore import *

from project.controllers.controller_canvas import CanvasController
from project.controllers.controller_panel import PanelController
from project.map_gen import MapGenerator


class AppController(QObject):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self._panel_controller = PanelController()
        self._canvas_controller = CanvasController()

        self._map_size = 7
        self._generator = MapGenerator(self._map_size)
