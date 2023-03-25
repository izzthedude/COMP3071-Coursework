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
        self._mapgen = MapGenerator(CANVAS_SIZE // size, size)
        self._panel.size_spinbox.setValue(size)
        self._panel.size_spinbox.valueChanged.connect(self._on_size_changed)

        start_x, start_y = self._calculate_vehicle_start()
        self._vehicle = Vehicle(start_x, start_y, VEHICLE_SIZE, VEHICLE_SIZE, 90)
        self._canvas: CanvasView = CanvasView(self._mapgen, self._vehicle,
                                              [None for _ in range(len(self._vehicle.sensors))])
        self._window.centralWidget().layout().addWidget(self._canvas)

        self._timer: QTimer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._is_running: bool = False

        self._panel.reset_btn.clicked.connect(self._on_reset)
        self._panel.regenerate_button.clicked.connect(self._on_regenerate)
        self._window.space_shortcut.activated.connect(self._on_startstop)

    def _tick(self):
        # Move vehicle
        self._vehicle.move()

        # Find intersection points
        # NOTE: for some reason this doesn't detect some intersections at seemingly random ticks. really no clue why
        self._intersections = {sensor: None for sensor in self._vehicle.sensors}
        tiles = self._mapgen.get_tiles()
        for i, sensor in enumerate(self._vehicle.sensors):
            first_intersected = False
            for j, tile in enumerate(tiles):
                if first_intersected:
                    break
                for k, border in enumerate(tile.borders):
                    if border:
                        if intersects := sensor.intersects(border, self._vehicle.theta):
                            self._intersections[sensor] = intersects
                            first_intersected = True
                            break

        self._recreate_canvas()

    def _recreate_canvas(self, reset: bool = False):
        self._window.centralWidget().layout().removeWidget(self._canvas)
        self._canvas.deleteLater()
        del self._canvas

        self._canvas = CanvasView(self._mapgen, self._vehicle, list(self._intersections.values()))
        self._window.centralWidget().layout().addWidget(self._canvas)

    def _calculate_vehicle_start(self):
        first_tile = self._mapgen.get_tiles()[0]
        x = first_tile.x + (first_tile.size / 2)
        y = 0 + (VEHICLE_SIZE / 2)
        return x, y

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
