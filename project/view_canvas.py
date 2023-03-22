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
        # Since the painter is translated to the center of the vehicle,
        # we need to account for that when drawing the other parts of the vehicle as well.
        # Hence, why you'll see `part.x - self._vehicle.x` when drawing the vehicle parts.
        painter.translate(self._vehicle.x, self._vehicle.y)
        painter.rotate(math.degrees(self._vehicle.theta))

        # Draw main body
        painter.fillRect(
            0 - self._vehicle.width / 2,
            0 - self._vehicle.height / 2,
            self._vehicle.width,
            self._vehicle.height,
            "blue"
        )

        # Draw wheels
        for wheel in self._vehicle.wheels:
            self._draw_wheel(wheel, painter)

        # Draw sensors
        brush = QBrush()
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        brush.setColor("yellow")
        painter.setBrush(brush)
        for sensor in self._vehicle.sensors:
            self._draw_sensor(sensor, painter)

    def _draw_wheel(self, wheel: Wheel, painter: QPainter):
        painter.fillRect(
            wheel.x - self._vehicle.x - wheel.width / 2,
            wheel.y - self._vehicle.y - wheel.height / 2,
            wheel.width,
            wheel.height,
            "black"
        )

    def _draw_sensor(self, sensor: Sensor, painter: QPainter):
        x = sensor.x - self._vehicle.x - sensor.radius / 2
        y = sensor.y - self._vehicle.y - sensor.radius / 2

        # Draw sensor lines
        painter.setPen("red")
        line = QLineF()
        line.setP1(QPointF(x + 4, y + 4))
        line.setAngle(-sensor.sense_angle)
        line.setLength(200)
        painter.drawLine(line)

        # Draw sensor
        painter.setPen("black")
        painter.drawEllipse(
            x,
            y,
            sensor.radius,
            sensor.radius
        )
