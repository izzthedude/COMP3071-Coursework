from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from project.enums import Sizes
from project.map_gen import MapTile, MapGenerator
from project.models import Vehicle


class CanvasView(QWidget):
    def __init__(self, mapgen: MapGenerator, vehicle: Vehicle, parent: QObject = None):
        super().__init__(parent)

        self.setFixedSize(Sizes.CANVAS_SIZE, Sizes.CANVAS_SIZE)
        self._tiles: list[MapTile] = mapgen.get_tiles()
        self._vehicle: Vehicle = vehicle

    def paintEvent(self, event):
        p = QPainter(self)
        self._draw_tiles(p)
        p.save()
        self._vehicle.draw(p)
        p.restore()

    def _draw_tiles(self, painter: QPainter):
        for tile in self._tiles:
            for border in tile.borders:
                if border is not None:
                    start, end = border
                    x_start, y_start = start
                    x_end, y_end = end
                    painter.drawLine(
                        x_start,
                        y_start,
                        x_end,
                        y_end
                    )
