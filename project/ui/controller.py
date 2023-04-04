from PySide6.QtCore import *
from PySide6.QtGui import *

from project.agent import NavigatorAgent
from project.enums import *
from project.environment import Environment, VehicleData
from project.models import Vehicle
from project.ui.canvas import Canvas
from project.ui.panel import Panel
from project.ui.window import MainWindow


class AppController(QObject):
    def __init__(self, environment: Environment, window: MainWindow, parent: QObject = None):
        super().__init__(parent)
        self._window: MainWindow = window
        self._panel: Panel = self._window.panel

        self._environment = environment
        self._mapgen = environment.mapgen
        self._vehicles: dict[Vehicle, VehicleData] = environment.vehicles

        self._is_running: bool = False

        self._canvas: Canvas = Canvas(self._mapgen, self._vehicles, self._is_running)
        self._timer: QTimer = QTimer(self)
        self._canvas_updater: QTimer = QTimer(self)  # The 'renderer' timer: runs on a different thread/timer.

        self._window.centralWidget().layout().addWidget(self._canvas)
        self._panel.size_spinbox.setValue(self._mapgen.get_map_size())

        self._window.key_pressed.connect(self._on_key_pressed)
        self._panel.reset_btn.clicked.connect(self._on_reset)
        self._panel.size_spinbox.valueChanged.connect(self._on_size_changed)
        self._panel.regenerate_button.clicked.connect(self._on_regenerate)

        self._timer.timeout.connect(self._tick)
        self._canvas_updater.timeout.connect(self._update_canvas)
        self._canvas_updater.start(1000 / 30)  # Canvas updates per second, adjust the denominator to the desired FPS.

    def _tick(self):
        self._environment.tick()

    def _on_key_pressed(self, event: QKeyEvent, code: int):
        event_type = event.type()

        if code == Qt.Key.Key_Space and event_type == QEvent.KeyPress:
            if self._is_running:
                self._timer.stop()
            else:
                self._timer.start(TICK_MS)
            self._is_running = not self._is_running

    def _on_size_changed(self, value: int):
        self._environment.on_size_changed(value)

    def _on_reset(self):
        self._environment.on_reset()

    def _on_regenerate(self):
        self._environment.on_regenerate()

    def _update_canvas(self):
        self._canvas.tiles = self._mapgen.get_tiles()
        self._canvas.is_running = self._is_running
        self._canvas.update()
