import math

from PySide6.QtCore import *
from PySide6.QtGui import *

from project.agent import NavigatorAgent
from project.enums import *
from project.map_gen import MapGenerator, MapTile
from project.models import Vehicle
from project.utils import distance_2p
from project.view_canvas import CanvasView
from project.view_panel import ControlPanel
from project.window_main import MainWindow


class AppController(QObject):
    def __init__(self, window: MainWindow, parent: QObject = None):
        super().__init__(parent)
        self._window: MainWindow = window
        self._panel: ControlPanel = self._window.panel

        size = 7
        self._mapgen = MapGenerator(CANVAS_SIZE // size, size)
        self._panel.size_spinbox.setValue(size)

        start_x, start_y = self._calculate_vehicle_start()
        self._vehicle = Vehicle(start_x, start_y, VEHICLE_SIZE, VEHICLE_SIZE, 90)
        self._vehicle.change_speed(1, 1)
        self._dspeed = 0.1
        self._turn_multiplier = 10
        self._dtheta_domain = (-math.pi, math.pi)
        self._dspeed_domain = (-self._dspeed * self._turn_multiplier, self._dspeed * self._turn_multiplier)

        self._panel.change_speed_spinbox.setRange(0.1, 2.0)
        self._panel.change_speed_spinbox.setSingleStep(0.05)
        self._panel.change_speed_spinbox.setValue(self._dspeed)
        self._panel.turn_multiplier_spinbox.setRange(1, 20)
        self._panel.turn_multiplier_spinbox.setSingleStep(1)
        self._panel.turn_multiplier_spinbox.setValue(self._turn_multiplier)

        self._intersections: dict = {sensor: (0.0, 0.0, 0.0) for sensor in self._vehicle.sensors}
        self._canvas: CanvasView = CanvasView(self._mapgen, self._vehicle, list(self._intersections.values()), False)
        self._window.centralWidget().layout().addWidget(self._canvas)

        self._timer: QTimer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._is_running: bool = False

        self._agent: NavigatorAgent = NavigatorAgent(self._vehicle, 150)
        self._is_training: bool = False

        self._window.key_pressed.connect(self._on_key_pressed)
        self._panel.reset_btn.clicked.connect(self._on_reset)
        self._panel.size_spinbox.valueChanged.connect(self._on_size_changed)
        self._panel.regenerate_button.clicked.connect(self._on_regenerate)
        self._panel.change_speed_spinbox.valueChanged.connect(self._on_dspeed_changed)
        self._panel.turn_multiplier_spinbox.valueChanged.connect(self._on_turn_multiplier_changed)
        self._panel.training_mode_btn.stateChanged.connect(self._on_training_mode_changed)

    def _tick(self):
        # Find intersection points
        tiles = self._closest_tiles()
        for i, sensor in enumerate(self._vehicle.sensors):
            first_intersected = False
            for j, tile in enumerate(tiles):
                if first_intersected:
                    break
                for k, border in enumerate(tile.borders):
                    if border is not None:
                        if intersects := sensor.intersects(border, self._vehicle.theta):
                            self._intersections[sensor] = intersects
                            first_intersected = True
                            break

        # Determine speed and direction using agent
        inputs = [distance for _, _, distance in self._intersections.values()]
        lspeed, rspeed = self._agent.determine(inputs)
        self._vehicle.set_lspeed(lspeed)
        self._vehicle.set_rspeed(rspeed)

        # Move vehicle and recreate canvas
        self._vehicle.move()
        self._recreate_canvas()

    def _on_key_pressed(self, event: QKeyEvent, code: int):
        event_type = event.type()

        if code == Qt.Key.Key_Space and event_type == QEvent.KeyPress:
            if self._is_running:
                self._timer.stop()
            else:
                self._timer.start(TICK_MS)
            self._is_running = not self._is_running

        if code == Qt.Key.Key_W and event_type == QEvent.KeyPress:
            self._vehicle.change_speed(self._dspeed, self._dspeed)

        if code == Qt.Key.Key_S and event_type == QEvent.KeyPress:
            self._vehicle.change_speed(-self._dspeed, -self._dspeed)

        turn_speed = self._dspeed * self._turn_multiplier
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

        self._recreate_canvas()

    def _on_startstop(self):
        if self._is_running:
            self._timer.stop()
        else:
            self._timer.start(TICK_MS)
        self._is_running = not self._is_running

    def _on_size_changed(self, value: int):
        self._mapgen.set_map_size(value)
        self._mapgen.set_tile_size(CANVAS_SIZE / value)

    def _on_reset(self):
        self._vehicle.x, self._vehicle.y = self._calculate_vehicle_start()
        self._vehicle.reset()
        self._recreate_canvas()

    def _on_regenerate(self):
        self._mapgen.regenerate()
        self._recreate_canvas()

    def _on_dspeed_changed(self, value: float):
        self._dspeed = value

    def _on_turn_multiplier_changed(self, value: float):
        self._turn_multiplier = value

    def _on_training_mode_changed(self, state: bool):
        self._is_training = bool(state)

    def _recreate_canvas(self):
        self._window.centralWidget().layout().removeWidget(self._canvas)
        self._canvas.deleteLater()
        del self._canvas

        self._canvas = CanvasView(self._mapgen, self._vehicle, list(self._intersections.values()), self._is_running)
        self._window.centralWidget().layout().addWidget(self._canvas)

    def _calculate_vehicle_start(self):
        first_tile = self._mapgen.get_tiles()[0]
        x = first_tile.x + (first_tile.size / 2)
        y = 0 + (VEHICLE_SIZE / 2)
        return x, y

    def _closest_tiles(self):
        def _distance(tile: MapTile):
            tile_center = tile.x + (tile.size / 2), tile.y + (tile.size / 2)
            return distance_2p(tile_center, (self._vehicle.x, self._vehicle.y))

        tiles = self._mapgen.get_tiles()
        closest = sorted(tiles, key=_distance)
        return closest
