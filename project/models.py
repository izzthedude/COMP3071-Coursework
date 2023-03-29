import math

from project import utils
from project.enums import *


class Wheel:
    def __init__(self, x: float, y: float, width: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = self.width * 3
        self.speed: float = 0.0


class Sensor:
    def __init__(self, x: float, y: float, size: float, sense_angle: float):
        self.x = x
        self.y = y
        self.size = size
        self.sense_length = CANVAS_SIZE
        self.sense_angle = sense_angle  # In RADIANS

    def line_start(self):
        return self.x, self.y

    def line_end(self, angle_offset: float = 0):
        return utils.point_on_circle(self.line_start(), self.sense_length, self.sense_angle + angle_offset)

    def intersects(self, line: tuple[tuple[int, int], tuple[int, int]], angle_offset: float = 0):
        sensor_line = (self.line_start(), self.line_end(angle_offset))

        # Code taken from https://gist.github.com/kylemcdonald/6132fc1c29fd3767691442ba4bc84018
        (x1, y1), (x2, y2) = sensor_line
        (x3, y3), (x4, y4) = line

        denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        if denom == 0:  # parallel
            return None

        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
        if not (0 < ua < 1):  # out of range
            return None

        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
        if not (0 < ub < 1):  # out of range
            return None

        x = x1 + ua * (x2 - x1)
        y = y1 + ua * (y2 - y1)
        return x, y, utils.distance_2p(self.line_start(), (x, y))

    def __repr__(self):
        return f"Sensor({int(self.x)},{int(self.y)})"


class Vehicle:
    def __init__(self, x: float, y: float, width: float, height: float, angle: float):
        self.x: float = x  # x and y are the CENTER point of the vehicle
        self.y: float = y
        self.width: float = width
        self.height: float = height
        self.theta: float = math.radians(angle)  # theta is in RADIANS, but I converted it from degrees for readability
        self.max_speed: float = 5

        # Wheels and Sensors are initially positioned as if the robot's angle is 0 degrees.
        # This will later be adjusted.

        # Wheels
        wheel_width = self.width / 6
        self.wheels: list[Wheel] = [
            Wheel(self.x, self.y - self.height / 2, wheel_width),
            Wheel(self.x, self.y + self.height / 2, wheel_width)
        ]

        # Sensors
        sensor_x = self.x + self.width / 2
        sensor_size = self.width / 6
        sense_angle = math.radians(45)
        self.sensors: list[Sensor] = [
            Sensor(sensor_x, (self.y + (self.height / 2)) * 0.25, sensor_size, -sense_angle),
            Sensor(sensor_x, (self.y + (self.height / 2)) * 0.50, sensor_size, 0),
            Sensor(sensor_x, (self.y + (self.height / 2)) * 0.75, sensor_size, sense_angle),
            Sensor(self.x, self.y + self.height / 2, sensor_size, math.radians(90)),
            # Sensor(self.x - self.width / 2, (self.y + (self.height / 2)) * 0.66, sensor_size,
            #        -sense_angle + math.radians(180)),
            # Sensor(self.x - self.width / 2, (self.y + (self.height / 2)) * 0.33, sensor_size,
            #        sense_angle + math.radians(180)),
            Sensor(self.x, self.y - self.height / 2, sensor_size, math.radians(-90)),
        ]

        # Recalibrate positions
        self._wheel_info = {}
        self._sensor_info = {}
        for wheel in self.wheels:
            self._wheel_info[wheel] = self._calculate_part_info(wheel)
            wheel.x, wheel.y = self._calculate_position(*self._wheel_info[wheel])
        for sensor in self.sensors:
            self._sensor_info[sensor] = self._calculate_part_info(sensor)
            sensor.x, sensor.y = self._calculate_position(*self._sensor_info[sensor])

    def move(self):
        # Referenced and modified from https://www.youtube.com/watch?v=zHboXMY45YU
        dx, dy = utils.point_on_circle((0, 0), (self.wheels[0].speed + self.wheels[1].speed) / 2, self.theta)
        self.theta += (self.wheels[0].speed - self.wheels[1].speed) / self.width
        self.theta %= 2 * math.pi

        # Move car
        self.x += dx
        self.y += dy

        # Recalculate positions of vehicle parts
        self._recalculate_parts()

    def speed(self):
        return (self.lspeed() + self.rspeed()) / 2

    def lspeed(self):
        return self.wheels[0].speed

    def rspeed(self):
        return self.wheels[1].speed

    def set_lspeed(self, speed: float):
        sign = math.copysign(1, speed)
        self.wheels[0].speed = sign * min(self.max_speed, speed)

    def set_rspeed(self, speed: float):
        sign = math.copysign(1, speed)
        self.wheels[1].speed = sign * min(self.max_speed, speed)

    def change_speed(self, left: float, right: float):
        lspeed = self.lspeed() + left
        rspeed = self.rspeed() + right

        lspeed = min(self.max_speed, lspeed)
        rspeed = min(self.max_speed, rspeed)

        if -self.max_speed <= (lspeed + rspeed) / 2 <= self.max_speed:
            self.wheels[0].speed = lspeed
            self.wheels[1].speed = rspeed

    def reset(self):
        self.theta = math.radians(90)
        self._recalculate_parts()

    def _recalculate_parts(self):
        # Move wheels
        for i, wheel in enumerate(self.wheels):
            wheel.x, wheel.y = self._calculate_position(*self._wheel_info[wheel])
        # Move sensors
        for i, sensor in enumerate(self.sensors):
            sensor.x, sensor.y = self._calculate_position(*self._sensor_info[sensor])

    def _calculate_position(self, angle: float, distance: float):
        """
        Calculates the position of a point relative to the center of the vehicle.

        Parameters
        ----------
        angle: float
            The angle (in radians) of the point relative to the center.
        distance: float
            The distance between the center of the vehicle and the point.

        Returns
        -------
        tuple
            The x and y coordinates of the new position.
        """
        return utils.point_on_circle((self.x, self.y), distance, self.theta + angle)

    def _calculate_part_info(self, part: Wheel | Sensor):
        """
        Calculates some location information of a vehicle part RELATIVE to the center of the vehicle.
        This is intended to be used ONCE during initialisation.

        Returns
        -------
        tuple
            The angle (in radians) and distance of the part from the center.
        """
        angle = math.atan2(part.y - self.y, part.x - self.x)
        distance = utils.distance_2p((self.x, self.y), (part.x, part.y))
        return angle, distance
