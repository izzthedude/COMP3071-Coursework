import math

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from project.enums import *
from project.map_gen import MapTile, MapGenerator
from project.models import Vehicle, Wheel, Sensor


class CanvasView(QWidget):
    def __init__(self, mapgen: MapGenerator, vehicle: Vehicle, parent: QObject = None):
        super().__init__(parent)

        self.setFixedSize(CANVAS_SIZE, CANVAS_SIZE)
        self._tiles: list[MapTile] = mapgen.get_tiles()
        self._vehicle: Vehicle = vehicle

    def paintEvent(self, event):
        p = QPainter(self)
        self._draw_tiles(p)
        p.save()
        self._draw_vehicle(p)
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

    def _draw_vehicle(self, painter: QPainter):
        # Draw main body
        painter.translate(self._vehicle.x, self._vehicle.y)
        painter.rotate(math.degrees(self._vehicle.theta))
        painter.fillRect(
            0 - self._vehicle.width / 2,
            0 - self._vehicle.height / 2,
            self._vehicle.width,
            self._vehicle.height,
            "blue"
        )
        painter.resetTransform()

        # Draw wheels
        for wheel in self._vehicle.wheels:
            self._draw_wheel(wheel, painter)
            painter.resetTransform()

        # Draw sensors
        brush = QBrush()
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        brush.setColor("yellow")
        painter.setBrush(brush)
        for sensor in self._vehicle.sensors:
            self._draw_sensor(sensor, painter)
            painter.resetTransform()

    def _draw_wheel(self, wheel: Wheel, painter: QPainter):
        painter.translate(wheel.x, wheel.y)
        painter.rotate(math.degrees(self._vehicle.theta))
        painter.fillRect(
            0 - wheel.width / 2,
            0 - wheel.height / 2,
            wheel.width,
            wheel.height,
            "black"
        )

    def _draw_sensor(self, sensor: Sensor, painter: QPainter):
        # Draw sensor lines
        painter.setPen("red")
        line = QLineF()
        line.setP1(QPointF(*sensor.line_start()))
        line.setP2(QPointF(*sensor.line_end(self._vehicle.theta)))
        painter.drawLine(line)

        # Draw sensor
        painter.setPen("black")
        painter.drawEllipse(
            sensor.x - sensor.size / 2,
            sensor.y - sensor.size / 2,
            sensor.size,
            sensor.size
        )
