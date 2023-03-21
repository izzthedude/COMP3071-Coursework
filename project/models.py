from PySide6.QtGui import *
from PySide6.QtCore import *

from project.enums import Sizes
from project.map_gen import MapTile


class Wheel:
    def __init__(self, x_offset: int, y_offset: int):
        self.width = Sizes.VEHICLE_SIZE / 4
        self.height = self.width * 1.5
        self.x_offset = x_offset + (self.width / 2)
        self.y_offset = y_offset + (self.height / 2)
        self.speed: float = 0.0


class Sensor:
    def __init__(self, x_offset: int, y_offset: int, sense_angle: int):
        self.radius = Sizes.VEHICLE_SIZE / 6
        self.x_offset = x_offset + (self.radius / 2)
        self.y_offset = y_offset + (self.radius / 2)
        self.angle_offset = sense_angle


class Vehicle:
    def __init__(self, x: int, y: int):
        self.x = x  # x and y are the CENTER point of the vehicle
        self.y = y
        self.width = Sizes.VEHICLE_SIZE
        self.height = Sizes.VEHICLE_SIZE
        self.angle = 180
        self.speed = 5

        self.wheel_left = Wheel(self.width / 2, 0)
        self.wheel_right = Wheel(-self.width / 2, 0)
        self.sensor_left = Sensor(self.width / 3, self.height / 2, -40)
        self.sensor_right = Sensor(-self.width / 3, self.height / 2, 40)

    def draw(self, painter: QPainter):
        painter.translate(self.x, self.y)
        painter.rotate(self.angle)

        # Draw main body
        painter.fillRect(
            0 - (self.width / 2),
            0 - (self.height / 2),
            self.width,
            self.height,
            "blue"
        )

        # Draw wheels
        self._draw_wheel(self.wheel_left, painter)
        self._draw_wheel(self.wheel_right, painter)

        # Draw sensors
        brush = QBrush()
        brush.setColor("yellow")
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        self._draw_sensor(self.sensor_left, painter)
        self._draw_sensor(self.sensor_right, painter)

    def move(self):
        self.y += 1

    def sense_tile_borders(self, tile: MapTile):
        pass

    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y

    def contains(self, x: int, y: int):
        start_x = self.x - (self.width / 2)
        start_y = self.y - (self.height / 2)
        return start_x < x < (start_x + self.width) and start_y < y < (start_y + self.height)

    def _draw_wheel(self, wheel: Wheel, painter: QPainter):
        painter.fillRect(
            0 - wheel.x_offset,
            0 - wheel.y_offset,
            wheel.width,
            wheel.height,
            "black"
        )

    def _draw_sensor(self, sensor: Sensor, painter: QPainter):
        x = 0 - sensor.x_offset
        y = 0 - sensor.y_offset
        painter.drawEllipse(
            x,
            y,
            sensor.radius,
            sensor.radius
        )

        painter.setPen("red")
        line = QLineF()
        line.setP1(QPointF(x+4, y))
        line.setAngle(90 - sensor.angle_offset)
        line.setLength(200)
        painter.drawLine(line)
        painter.setPen("black")
