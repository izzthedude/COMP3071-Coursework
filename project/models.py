import math

from project.enums import *


class Wheel:
    def __init__(self, x_offset: float, y_offset: float):
        self.width = VEHICLE_SIZE / 2
        self.height = self.width / 3
        self.x_offset = x_offset - self.width / 2
        self.y_offset = y_offset - self.height / 2
        self.speed: float = 0.0


class Sensor:
    def __init__(self, x_offset: float, y_offset: float, sense_angle: float):
        self.radius = VEHICLE_SIZE / 6
        self.x_offset = x_offset - (self.radius / 2)
        self.y_offset = y_offset - (self.radius / 2)
        self.angle_offset = sense_angle


class Vehicle:
    def __init__(self, x: float, y: float):
        self.x: float = x  # x and y are the CENTER point of the vehicle
        self.y: float = y
        self.width: float = VEHICLE_SIZE
        self.height: float = VEHICLE_SIZE
        self.theta: float = math.radians(90)
        self.max_speed: float = 5

        self.wheels: list[Wheel] = [
            Wheel(self.width / 2, 0),
            Wheel(self.width / 2, self.height)
        ]
        self.wheels[0].speed = 2
        self.wheels[1].speed = -2

        angle_offset = 45
        self.sensors: list[Sensor] = [
            Sensor(self.width, self.height * 0.25, -angle_offset),
            Sensor(self.width, self.height * 0.5, 0),
            Sensor(self.width, self.height * 0.75, angle_offset)
        ]

    def move(self):
        self.x += ((self.wheels[0].speed + self.wheels[1].speed) / 2) * math.cos(self.theta)
        self.y += ((self.wheels[0].speed + self.wheels[1].speed) / 2) * math.sin(self.theta)
        self.theta += (self.wheels[0].speed - self.wheels[1].speed) / (self.width * 1)
        self.theta %= 2 * math.pi
