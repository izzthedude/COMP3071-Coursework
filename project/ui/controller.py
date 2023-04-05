from PySide6.QtCore import *
from PySide6.QtGui import *

from project import enums
from project.environment import Environment
from project.models import Vehicle, VehicleData
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
        self._vehicles: dict[Vehicle, VehicleData] = environment.vehicle_datas

        self._is_running: bool = False

        self._canvas: Canvas = Canvas(self._mapgen, self._vehicles, self._is_running)
        self._timer: QTimer = QTimer(self)
        self._canvas_updater: QTimer = QTimer(self)  # The 'renderer' timer: runs on a different thread/timer.
        self._window.centralWidget().layout().addWidget(self._canvas)

        self._panel.update_interval_spinbox.setRange(1, 30)
        self._panel.update_interval_spinbox.setValue(enums.TICK_MS)
        self._panel.auto_reset_checkbox.setChecked(self._environment.auto_reset)
        self._panel.learning_mode_checkbox.setChecked(self._environment.learning_mode)
        self._panel.size_spinbox.setRange(3, 11)
        self._panel.size_spinbox.setValue(self._mapgen.get_map_size())

        self._window.key_pressed.connect(self._on_key_pressed)
        self._panel.update_interval_spinbox.valueChanged.connect(self._on_update_interval_changed)
        self._panel.auto_reset_checkbox.stateChanged.connect(self._on_auto_reset_changed)
        self._panel.size_spinbox.valueChanged.connect(self._on_size_changed)
        self._panel.regenerate_button.clicked.connect(self._on_regenerate)
        self._panel.vehicle_reset_btn.clicked.connect(self._on_reset_vehicle)
        self._panel.learning_mode_checkbox.stateChanged.connect(self._on_learning_mode_changed)

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
                self._timer.start(enums.TICK_MS)
            self._is_running = not self._is_running

        if code == Qt.Key.Key_Return and event_type == QEvent.KeyPress:
            self._environment.on_generation_end()
            self._environment.on_reset_vehicle()

    def _on_update_interval_changed(self, value: int):
        enums.TICK_MS = value

    def _on_auto_reset_changed(self, check: bool):
        self._environment.auto_reset = check

    def _on_size_changed(self, value: int):
        self._environment.on_size_changed(value)

    def _on_regenerate(self):
        self._environment.on_regenerate()

    def _on_reset_vehicle(self):
        self._environment.on_reset_vehicle()

    def _on_learning_mode_changed(self, check: bool):
        self._environment.learning_mode = check

    def _on_save_best_model(self):
        self._environment.on_save_best_model()

    def _on_load_model(self):
        # self._environment.on_load_model()
        pass

    def _update_canvas(self):
        self._canvas.tiles = self._mapgen.get_tiles()
        self._canvas.is_running = self._is_running
        self._canvas.generation = self._environment.generation
        self._canvas.update()
