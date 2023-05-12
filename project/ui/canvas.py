import math

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from project import enums
from project.environment import Environment
from project.map_gen import MapTile
from project.models import Vehicle, Wheel, Sensor, VehicleData
from project.types import *


class Canvas(QWidget):
    def __init__(self, environment: Environment, is_running: bool, parent: QObject = None):
        super().__init__(parent)

        self.setFixedSize(enums.CANVAS_SIZE, enums.CANVAS_SIZE)
        self._env: Environment = environment
        self.is_running: bool = is_running

    def paintEvent(self, event):
        p = QPainter(self)

        # Draw last tile
        p.save()
        p.setOpacity(0.4)
        last_tile = self._env.mapgen.tiles()[-1]
        p.fillRect(
            last_tile.x,
            last_tile.y,
            last_tile.size,
            last_tile.size,
            "green"
        )
        p.restore()

        # Draw tile borders
        for tile in self._env.mapgen.tiles():
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
        for vehicle, (_, data) in self._env.vehicles.items():
            if vehicle is not self._env.current_best_vehicle:
                self._draw_vehicle(vehicle, data, "blue", p)

        # Always draw the best vehicle on top
        if best := self._env.current_best_vehicle:
            self._draw_vehicle(best, self._env.vehicle_data(best), "green", p)

        # Draw controls info
        controls_info = [
            f"SPACE: Run/stop simulation",
            f"ENTER: Proceed to next generation"
        ]
        self._draw_text_section(0, 0, "Controls", controls_info, p)

        # Draw general info
        ticks_left = self._env.ticks_per_gen - self._env.current_ticks
        until_regen = self._env.regen_n_runs - self._env.current_map_run
        until_resize = self._env.resize_n_regens - self._env.current_mapsize_run
        general_info = [
            f"Running: {self.is_running} | {ticks_left}",
            f"Generation: {self._env.generation} | {until_regen} | {until_resize}",
        ]
        self._draw_text_section(850, 0, "", general_info, p)

    def _draw_tile(self, tile: MapTile, painter: QPainter):
        for border in tile.borders:
            if border:
                start, end = border
                x_start, y_start = start
                x_end, y_end = end
                painter.drawLine(
                    x_start,
                    y_start,
                    x_end,
                    y_end
                )

    def _draw_vehicle(self, vehicle: Vehicle, data: VehicleData, body_colour: str, painter: QPainter):
        # Draw vehicle's main body
        painter.save()
        self._draw_vehicle_body(vehicle, data, body_colour, painter)
        painter.resetTransform()
        painter.restore()

        # Draw wheels
        for wheel in vehicle.wheels:
            self._draw_wheel(vehicle, wheel, painter)
            painter.resetTransform()

        # Draw sensor lines
        painter.save()
        for i in range(len(vehicle.sensors)):
            # TODO (low): Find out how to update sensor length in real time, instead of on ticks
            point, _ = data.intersections[i]
            if not (data.collision or data.is_finished):  # Only draw sensors of moving vehicles, to reduce visual mess
                self._draw_sensor_line(vehicle, vehicle.sensors[i], point, painter)
        painter.restore()

        # Draw sensors
        painter.save()
        for sensor in vehicle.sensors:
            self._draw_sensor(sensor, painter)
            painter.resetTransform()
        painter.restore()

    def _draw_vehicle_body(self, vehicle: Vehicle, data: VehicleData, color: str, painter: QPainter):
        # Draw vehicle's main body
        painter.translate(vehicle.x, vehicle.y)
        painter.rotate(math.degrees(vehicle.theta))
        painter.fillRect(
            0 - vehicle.width / 2,
            0 - vehicle.height / 2,
            vehicle.width,
            vehicle.height,
            color
        )

        # Draw border around vehicle's main body
        # Draw it red if collided
        if data.collision:
            painter.setPen("red")
        if data.is_finished:
            painter.setPen("lime")

        painter.drawRect(
            0 - vehicle.width / 2,
            0 - vehicle.height / 2,
            vehicle.width,
            vehicle.height,
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

    def _draw_sensor_line(self, vehicle: Vehicle, sensor: Sensor, end: Point, painter: QPainter):
        # Draw sensor lines
        painter.setPen("red")
        painter.setOpacity(0.4)

        line = QLineF()
        line.setP1(QPointF(*sensor.start()))
        line.setP2(QPointF(*end))
        line.setAngle(math.degrees(-vehicle.theta - sensor.theta))
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
