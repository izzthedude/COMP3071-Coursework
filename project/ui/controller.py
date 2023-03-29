from PySide6.QtCore import *
from PySide6.QtGui import *

from project.agent import NavigatorAgent
from project.enums import *
from project.environment import Environment
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
        self._vehicle = environment.vehicle
        self._agent: NavigatorAgent = environment.agent

        self._intersections: dict = environment.intersections
        self._is_running: bool = False

        self._canvas: Canvas = Canvas(self._mapgen, self._vehicle, list(self._intersections.values()),
                                      self._is_running)
        self._timer: QTimer = QTimer(self)

        self._window.centralWidget().layout().addWidget(self._canvas)
        self._panel.size_spinbox.setValue(self._mapgen.get_map_size())
        self._panel.change_speed_spinbox.setRange(0.1, 2.0)
        self._panel.change_speed_spinbox.setSingleStep(0.05)
        self._panel.change_speed_spinbox.setValue(self._environment.dspeed)
        self._panel.turn_multiplier_spinbox.setRange(1, 20)
        self._panel.turn_multiplier_spinbox.setSingleStep(1)
        self._panel.turn_multiplier_spinbox.setValue(self._environment.turn_multiplier)

        self._window.key_pressed.connect(self._on_key_pressed)
        self._panel.reset_btn.clicked.connect(self._on_reset)
        self._panel.size_spinbox.valueChanged.connect(self._on_size_changed)
        self._panel.regenerate_button.clicked.connect(self._on_regenerate)
        self._panel.change_speed_spinbox.valueChanged.connect(self._on_dspeed_changed)
        self._panel.turn_multiplier_spinbox.valueChanged.connect(self._on_turn_multiplier_changed)
        self._panel.manual_mode_btn.stateChanged.connect(self._on_manual_mode_changed)
        self._timer.timeout.connect(self._tick)

    def _tick(self):
        self._environment.tick()
        self._update_canvas()

    def _on_key_pressed(self, event: QKeyEvent, code: int):
        event_type = event.type()

        if code == Qt.Key.Key_Space and event_type == QEvent.KeyPress:
            if self._is_running:
                self._timer.stop()
            else:
                self._timer.start(TICK_MS)
            self._is_running = not self._is_running

        if code == Qt.Key.Key_W and event_type == QEvent.KeyPress:
            self._vehicle.change_speed(self._environment.dspeed / 2, self._environment.dspeed / 2)

        if code == Qt.Key.Key_S and event_type == QEvent.KeyPress:
            self._vehicle.change_speed(-self._environment.dspeed / 2, -self._environment.dspeed / 2)

        turn_speed = self._environment.dspeed * self._environment.turn_multiplier
        if code == Qt.Key.Key_A:
            if event_type == QEvent.KeyPress:
                self._vehicle.change_speed(-turn_speed, turn_speed)
            elif event_type == QEvent.KeyRelease:
                self._vehicle.change_speed(turn_speed, -turn_speed)

        if code == Qt.Key.Key_D:
            if event_type == QEvent.KeyPress:
                self._vehicle.change_speed(turn_speed, -turn_speed)
            elif event_type == QEvent.KeyRelease:
                self._vehicle.change_speed(-turn_speed, turn_speed)

        self._update_canvas()

    def _on_size_changed(self, value: int):
        self._environment.on_size_changed(value)

    def _on_reset(self):
        self._environment.on_reset()
        self._update_canvas()

    def _on_regenerate(self):
        self._environment.on_regenerate()
        self._update_canvas()

    def _on_dspeed_changed(self, value: float):
        self._environment.dspeed = value

    def _on_turn_multiplier_changed(self, value: float):
        self._environment.turn_multiplier = value

    def _on_manual_mode_changed(self, state: bool):
        self._environment.is_manual = bool(state)

    def _update_canvas(self):
        self._canvas.tiles = self._mapgen.get_tiles()
        self._canvas.intersections = list(self._intersections.values())
        self._canvas.is_running = self._is_running
        self._canvas.update()
