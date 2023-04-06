import math

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from project.enums import CANVAS_SIZE
from project.environment import Environment
from project.map_gen import MapTile
from project.models import Vehicle, Wheel, Sensor


class Canvas(QWidget):
    def __init__(self, environment: Environment, is_running: bool, parent: QObject = None):
        super().__init__(parent)

        self.setFixedSize(CANVAS_SIZE, CANVAS_SIZE)
        self._env: Environment = environment
        self.is_running: bool = is_running

    def paintEvent(self, event):
        p = QPainter(self)

        # Draw last tile
        p.save()
        p.setOpacity(0.4)
        last_tile = self._env.mapgen.get_tiles()[-1]
        p.fillRect(
            last_tile.x,
            last_tile.y,
            last_tile.size,
            last_tile.size,
            "green"
        )
        p.restore()

        # Draw tile borders
        for tile in self._env.mapgen.get_tiles():
            self._draw_tile(tile, p)

        # Draw finish line for last border
        p.save()
        pen = p.pen()
        pen.setWidth(3)
        pen.setStyle(Qt.PenStyle.DashDotLine)
        p.setPen(pen)
        p1, p2 = last_tile.finish_line()
        p.drawLine(*p1, *p2)
        p.restore()

        # Draw vehicles
        for vehicle, data in self._env.vehicle_datas.items():
            # Draw vehicle's main body
            p.save()
            p.translate(vehicle.x, vehicle.y)
            p.rotate(math.degrees(vehicle.theta))
            p.fillRect(
                0 - vehicle.width / 2,
                0 - vehicle.height / 2,
                vehicle.width,
                vehicle.height,
                "blue"
            )

            # Draw border around vehicle's main body
            # Draw it red if collided
            if data.collision:
                p.setPen("red")
            if data.is_finished:
                p.setPen("lime")

            p.drawRect(
                0 - vehicle.width / 2,
                0 - vehicle.height / 2,
                vehicle.width,
                vehicle.height,
            )
            p.resetTransform()
            p.restore()

            # Draw wheels
            for wheel in vehicle.wheels:
                self._draw_wheel(vehicle, wheel, p)
                p.resetTransform()

            # Draw sensor lines
            p.save()
            for i in range(len(vehicle.sensors)):
                length = vehicle.sensors[i].sense_length
                if data.intersections and data.intersections[i]:
                    _, _, length = data.intersections[i]
                self._draw_sensor_line(vehicle, vehicle.sensors[i], length, p)
            p.restore()

            # Draw sensors
            p.save()
            for sensor in vehicle.sensors:
                self._draw_sensor(sensor, p)
                p.resetTransform()
            p.restore()

        # Draw info
        is_running = "(RUNNING)" if self.is_running else "(STOPPED)"
        info = [
            f"Generation: {self._env.generation}"
        ]
        self._draw_text_section(0, 0, f"Press SPACE to start/stop the timer {is_running}", info, p)

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

    def _draw_wheel(self, vehicle: Vehicle, wheel: Wheel, painter: QPainter):
        painter.translate(wheel.x, wheel.y)
        painter.rotate(math.degrees(vehicle.theta) + 90)
        painter.fillRect(
            0 - wheel.width / 2,
            0 - wheel.height / 2,
            wheel.width,
            wheel.height,
            "black"
        )

    def _draw_sensor_line(self, vehicle: Vehicle, sensor: Sensor, length: float, painter: QPainter):
        # Draw sensor lines
        painter.setPen("red")
        painter.setOpacity(0.4)

        line = QLineF()
        line.setP1(QPointF(*sensor.line_start()))
        line.setAngle(math.degrees(-vehicle.theta - sensor.sense_angle))
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
