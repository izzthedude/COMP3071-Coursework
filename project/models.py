from PySide6.QtGui import QPainter

from project.enums import Sizes
from project.map_gen import MapTile


class Vehicle:
    def __init__(self, x: int, y: int):
        self.x = x  # x and y are the CENTER point of the vehicle
        self.y = y
        self.size = Sizes.VEHICLE_SIZE
        self.angle = 180

    def draw(self, painter: QPainter):
        # Draw main body
        painter.translate(self.x, self.y)
        painter.fillRect(
            0 - (self.size // 2),
            0 - (self.size // 2),
            self.size,
            self.size,
            "blue"
        )

    def move(self):
        self.y += 1

    def sense_tile_borders(self, tile: MapTile):
        pass

    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y

    def contains(self, x: int, y: int):
        start_x = self.x - (self.size / 2)
        start_y = self.y - (self.size / 2)
        return start_x < x < (start_x + self.size) and start_y < y < (start_y + self.size)
