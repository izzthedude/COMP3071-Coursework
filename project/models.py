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
        self.sense_angle = sense_angle


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
        sense_angle = 45
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
