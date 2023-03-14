from PySide6.QtCore import *

from project.map_gen import MapGenerator
from project.view_canvas import CanvasView
from project.view_panel import ControlPanel
from project.window_main import MainWindow


class AppController(QObject):
    def __init__(self, window: MainWindow, parent: QObject = None):
        super().__init__(parent)
        self._window: MainWindow = window
        self._panel: ControlPanel = self._window.panel
        self._canvas: CanvasView = self._window.canvas

        size = 7
        self._generator = MapGenerator(size)
        self._panel.size_spinbox.setValue(size)

        self._panel.size_spinbox.valueChanged.connect(self._on_size_changed)
        self._panel.regenerate_button.clicked.connect(self._on_regenerate)

    def _on_size_changed(self, value: int):
        self._generator.set_size(value)

    def _on_regenerate(self):
        self._generator.regenerate()
