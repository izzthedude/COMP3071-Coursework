import math

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from project.enums import CANVAS_SIZE
from project.map_gen import MapTile, MapGenerator
from project.models import Vehicle, Wheel, Sensor


class CanvasView(QWidget):
    def __init__(self, mapgen: MapGenerator, vehicle: Vehicle, intersections: list, is_running: bool, parent: QObject = None):
        super().__init__(parent)

        self.setFixedSize(CANVAS_SIZE, CANVAS_SIZE)
        self._tiles: list[MapTile] = mapgen.get_tiles()
        self._vehicle: Vehicle = vehicle
        self._intersections: list[tuple[float, float, float]] = intersections
        self._is_running: bool = is_running

    def paintEvent(self, event):
        p = QPainter(self)

        # Draw tiles
        for tile in self._tiles:
            self._draw_tile(tile, p)

        # Draw vehicle's main body
        p.translate(self._vehicle.x, self._vehicle.y)
        p.rotate(math.degrees(self._vehicle.theta))
        p.fillRect(
            0 - self._vehicle.width / 2,
            0 - self._vehicle.height / 2,
            self._vehicle.width,
            self._vehicle.height,
            "blue"
        )
        p.resetTransform()

        # Draw wheels
        for wheel in self._vehicle.wheels:
            self._draw_wheel(wheel, p)
            p.resetTransform()

        # Draw sensors
        brush = QBrush()
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        brush.setColor("yellow")
        p.setBrush(brush)
        for sensor in self._vehicle.sensors:
            self._draw_sensor(sensor, p)
            p.resetTransform()

        # Draw vehicle info
        self._draw_topleft_info(p)

        # Draw intersections info
        self._draw_topright_info(p, self._intersections)

    def _draw_tile(self, tile: MapTile, painter: QPainter):
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

    def _draw_wheel(self, wheel: Wheel, painter: QPainter):
        painter.translate(wheel.x, wheel.y)
        painter.rotate(math.degrees(self._vehicle.theta) + 90)
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
        painter.setOpacity(0.4)
        line = QLineF()
        line.setP1(QPointF(*sensor.line_start()))
        line.setP2(QPointF(*sensor.line_end(self._vehicle.theta)))
        painter.drawLine(line)
        painter.setOpacity(1)

        # Draw sensor
        painter.setPen("black")
        painter.drawEllipse(
            sensor.x - sensor.size / 2,
            sensor.y - sensor.size / 2,
            sensor.size,
            sensor.size
        )

    def _draw_topleft_info(self, painter: QPainter):
        # Draw start/stop instruction
        painter.save()
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)

        is_running = "(RUNNING)" if self._is_running else "(STOPPED)"
        font_height = QFontMetrics(font).height()
        x, y = 0, font_height
        painter.drawText(x, y, f"Press SPACE to start/stop the timer {is_running}")
        painter.restore()
        y += font_height

        # Draw vehicle info
        info = {
            "x": f"{self._vehicle.x:.2f}",
            "y": f"{self._vehicle.y:.2f}",
            "angle": f"{math.degrees(self._vehicle.theta):.2f}",
            "vl": f"{self._vehicle.lspeed(): .2f}",
            "vr": f"{self._vehicle.rspeed():.2f}",
            "speed": f"{self._vehicle.speed():.2f}"
        }
        font_height = QFontMetrics(painter.font()).height()
        for key, value in info.items():
            painter.drawText(x, y, f"{key}: {value}")
            y += font_height

    def _draw_topright_info(self, painter: QPainter, intersections: list):
        font_height = QFontMetrics(painter.font()).height()
        x, y = 750, font_height

        # Draw title
        painter.save()
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(x, y, "Sensors Intersections (x, y, distance)")
        painter.restore()

        y += font_height
        for i, info in enumerate(intersections):
            text = "-"
            if info:
                ix, iy, distance = info
                text = f"({ix:.2f},{iy:.2f},{distance:.2f})"
            painter.drawText(x, y, f"Sensor {i + 1}: {text}")
            y += font_height
