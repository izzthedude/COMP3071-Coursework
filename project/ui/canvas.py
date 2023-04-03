import math

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from project.enums import CANVAS_SIZE
from project.map_gen import MapTile, MapGenerator
from project.models import Vehicle, Wheel, Sensor


class Canvas(QWidget):
    def __init__(self, mapgen: MapGenerator, vehicle: Vehicle, is_running: bool,
                 parent: QObject = None):
        super().__init__(parent)

        self.setFixedSize(CANVAS_SIZE, CANVAS_SIZE)
        self.tiles: list[MapTile] = mapgen.get_tiles()
        self.vehicle: Vehicle = vehicle
        self.intersections: list[tuple[float, float, float]] = []
        self.collision: tuple[float, float] | None = None
        self.is_running: bool = is_running

    def paintEvent(self, event):
        p = QPainter(self)

        # Draw tiles
        for tile in self.tiles:
            self._draw_tile(tile, p)

        # Draw vehicle's main body
        p.translate(self.vehicle.x, self.vehicle.y)
        p.rotate(math.degrees(self.vehicle.theta))
        p.fillRect(
            0 - self.vehicle.width / 2,
            0 - self.vehicle.height / 2,
            self.vehicle.width,
            self.vehicle.height,
            "blue"
        )
        p.resetTransform()

        # Draw wheels
        for wheel in self.vehicle.wheels:
            self._draw_wheel(wheel, p)
            p.resetTransform()

        # Draw sensor lines
        p.save()
        for i in range(len(self.vehicle.sensors)):
            length = self.vehicle.sensors[i].sense_length
            if self.intersections and self.intersections[i]:
                _, _, length = self.intersections[i]
            self._draw_sensor_line(self.vehicle.sensors[i], length, p)
        p.restore()

        # Draw sensors
        p.save()
        for sensor in self.vehicle.sensors:
            self._draw_sensor(sensor, p)
            p.resetTransform()
        p.restore()

        # Draw collision
        if self.collision:
            p.save()
            p.setPen("red")
            size = 10
            x, y = self.collision[0] - size / 2, self.collision[1] - size / 2
            p.drawEllipse(x, y, size, size)
            p.restore()

        # Draw info
        is_running = "(RUNNING)" if self.is_running else "(STOPPED)"
        topleft_texts = [
            f"angle: {math.degrees(self.vehicle.theta):.2f}",
            f"speed: {self.vehicle.speed():.2f}"
        ]
        self._draw_text_section(0, 0, f"Press SPACE to start/stop the timer {is_running}", topleft_texts, p)

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
        painter.rotate(math.degrees(self.vehicle.theta) + 90)
        painter.fillRect(
            0 - wheel.width / 2,
            0 - wheel.height / 2,
            wheel.width,
            wheel.height,
            "black"
        )

    def _draw_sensor_line(self, sensor: Sensor, length: float, painter: QPainter):
        # Draw sensor lines
        painter.setPen("red")
        painter.setOpacity(0.4)

        line = QLineF()
        line.setP1(QPointF(*sensor.line_start()))
        line.setAngle(math.degrees(-self.vehicle.theta - sensor.sense_angle))
        line.setLength(length)
        painter.drawLine(line)
        painter.setOpacity(1)

    def _draw_sensor(self, sensor: Sensor, painter: QPainter):
        brush = QBrush()
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        brush.setColor("yellow")
        painter.setBrush(brush)

        # Draw sensor
        painter.setPen("black")
        painter.drawEllipse(
            sensor.x - sensor.size / 2,
            sensor.y - sensor.size / 2,
            sensor.size,
            sensor.size
        )

    def _draw_text_section(self, x: float, y: float, title: str, text_rows: list[str], painter: QPainter):
        font_height = QFontMetrics(painter.font()).height()

        if title:
            y += font_height
            painter.save()
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(x, y, title)
            painter.restore()

        y += font_height
        for text in text_rows:
            painter.drawText(x, y, text)
            y += font_height
