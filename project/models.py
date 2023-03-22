import math

from project.enums import *


class Wheel:
    def __init__(self, x: float, y: float, width: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = self.width / 3
        self.speed: float = 0.0


class Sensor:
    def __init__(self, x: float, y: float, radius: float, sense_angle: float):
        self.x = x
        self.y = y
        self.radius = radius
        self.sense_length = 200
        self.sense_angle = sense_angle  # In RADIANS

    def line_start(self):
        return self.x, self.y

    def line_end(self, angle_offset: float = 0):
        cum_angle = self.sense_angle + angle_offset
        end_x = self.sense_length * math.cos(cum_angle) + self.x
        end_y = self.sense_length * math.sin(cum_angle) + self.y
        return end_x, end_y

    def intersects(self, line: tuple[tuple[int, int], tuple[int, int]], angle_offset: float = 0):
        sensor_line = (self.line_start(), self.line_end(angle_offset))

        # Code taken from https://stackoverflow.com/a/20677983
        ydiff = (sensor_line[0][1] - sensor_line[1][1], line[0][1] - line[1][1])
        xdiff = (sensor_line[0][0] - sensor_line[1][0], line[0][0] - line[1][0])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            return

        d = (det(*sensor_line), det(*line))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div

        sensor_xs = [p[0] for p in sensor_line]
        sensor_ys = [p[1] for p in sensor_line]
        line_xs = [p[0] for p in line]
        line_ys = [p[1] for p in line]

        if min(sensor_xs) <= x <= max(sensor_xs) and min(sensor_ys) <= y <= max(sensor_ys) and \
                min(line_xs) <= x <= max(line_xs) and min(line_ys) <= y <= max(line_ys):
            print(f"({x, y}) : {sensor_xs} | {sensor_ys} | {line_xs} | {line_ys}")
            return x, y


class Vehicle:
    def __init__(self, x: float, y: float):
        self.x: float = x  # x and y are the CENTER point of the vehicle
        self.y: float = y
        self.width: float = VEHICLE_SIZE
        self.height: float = VEHICLE_SIZE
        self.theta: float = math.radians(90)  # theta is in RADIANS, but I converted it from degrees for readability
        self.max_speed: float = 5

        # Wheels
        wheel_width = VEHICLE_SIZE / 2
        self.wheels: list[Wheel] = [
            Wheel(self.x, self.y - self.height / 2, wheel_width),
            Wheel(self.x, self.y + self.height / 2, wheel_width)
        ]
        self.wheels[0].speed = 2
        self.wheels[1].speed = 2

        # Sensors
        sensor_x = self.x + self.width / 2
        sensor_radius = VEHICLE_SIZE / 6
        sense_angle = math.radians(45)
        self.sensors: list[Sensor] = [
            Sensor(sensor_x, (self.y + (self.height / 2)) * 0.25, sensor_radius, -sense_angle),
            Sensor(sensor_x, (self.y + (self.height / 2)) * 0.50, sensor_radius, 0),
            Sensor(sensor_x, (self.y + (self.height / 2)) * 0.75, sensor_radius, sense_angle)
        ]

    def move(self):
        # Referenced and modified from https://www.youtube.com/watch?v=zHboXMY45YU
        dx = ((self.wheels[0].speed + self.wheels[1].speed) / 2) * math.cos(self.theta)
        dy = ((self.wheels[0].speed + self.wheels[1].speed) / 2) * math.sin(self.theta)
        dtheta = (self.wheels[0].speed - self.wheels[1].speed) / (self.width * 1)

        # Move car
        self.x += dx
        self.y += dy
        self.theta += dtheta
        self.theta %= 2 * math.pi

        # Move wheels
        for wheel in self.wheels:
            wheel.x += dx
            wheel.y += dy

        # Move sensors
        for sensor in self.sensors:
            sensor.x += dx
            sensor.y += dy
