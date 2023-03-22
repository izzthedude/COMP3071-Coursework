from PySide6.QtCore import *

from project.enums import *
from project.map_gen import MapGenerator
from project.models import Vehicle
from project.view_canvas import CanvasView
from project.view_panel import ControlPanel
from project.window_main import MainWindow


class AppController(QObject):
    def __init__(self, window: MainWindow, parent: QObject = None):
        super().__init__(parent)
        self._window: MainWindow = window
        self._panel: ControlPanel = self._window.panel

        size = 7
        self._generator = MapGenerator(size)
        self._panel.size_spinbox.setValue(size)
        self._panel.size_spinbox.valueChanged.connect(self._on_size_changed)
        self._panel.regenerate_button.clicked.connect(self._on_regenerate)

        start_x, start_y = self._calculate_vehicle_start()
        self._vehicle = Vehicle(start_x, start_y)
        self._canvas: CanvasView = CanvasView(self._generator, self._vehicle)
        self._window.centralWidget().layout().addWidget(self._canvas)

        self._timer: QTimer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(TICK_MS)

    def _tick(self):
        self._vehicle.move()
        self._recreate_canvas()

    def _recreate_canvas(self):
        self._window.centralWidget().layout().removeWidget(self._canvas)
        self._canvas.deleteLater()
        del self._canvas

        self._canvas = CanvasView(self._generator, self._vehicle)
        self._window.centralWidget().layout().addWidget(self._canvas)

    def _calculate_vehicle_start(self):
        first_tile = self._generator.get_tiles()[0]
        x = first_tile.x + (first_tile.size / 2)
        y = 0 + (VEHICLE_SIZE / 2)
        return x, y

    def _on_size_changed(self, value: int):
        self._generator.set_size(value)

    def _on_regenerate(self):
        self._generator.regenerate()
        self._recreate_canvas()
