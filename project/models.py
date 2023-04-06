import math
from dataclasses import dataclass, asdict, field

from project import enums
from project import utils


class Wheel:
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed: float = 0.0


class Sensor:
    def __init__(self, x: float, y: float, size: float, sense_angle: float):
        self.x = x
        self.y = y
        self.size = size
        self.sense_length = 200
        self.sense_angle = sense_angle  # In RADIANS

    def line_start(self):
        return self.x, self.y

    def line_end(self, angle_offset: float = 0):
        return utils.point_on_circle(self.line_start(), self.sense_length, self.sense_angle + angle_offset)

    def intersects(self, line: tuple[tuple[int, int], tuple[int, int]], angle_offset: float = 0):
        sensor_line = (self.line_start(), self.line_end(angle_offset))

        intersection_point = utils.intersects(sensor_line, line)
        if not intersection_point:
            return None

        x, y = intersection_point
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

        # Wheels and Sensors will be initially positioned as if the robot's angle is 0 degrees, which faces the right.
        # This will later be recalibrated.

        # Wheels
        wheel_width, wheel_height = 8, 24
        self.wheels: list[Wheel] = [
            Wheel(self.x, self.y - self.height / 2, wheel_width, wheel_height),
            Wheel(self.x, self.y + self.height / 2, wheel_width, wheel_height)
        ]

        # Sensors
        sensor_size = 8
        sensor_x = self.x + self.width / 2
        end_y = self.y + self.height / 2
        y_offset = end_y - self.height
        front_sense_angle = math.radians(30)
        side_sense_angle = math.radians(60)
        self.sensors: list[Sensor] = [
            Sensor(sensor_x, (end_y - y_offset) * 0.25 + y_offset, sensor_size, -front_sense_angle),  # Front left
            Sensor(sensor_x, (end_y - y_offset) * 0.50 + y_offset, sensor_size, 0),  # Front center
            Sensor(sensor_x, (end_y - y_offset) * 0.75 + y_offset, sensor_size, front_sense_angle),  # Front right
            Sensor(self.x, self.y + self.height / 2, sensor_size, side_sense_angle),  # Right
            Sensor(self.x, self.y - self.height / 2, sensor_size, -side_sense_angle),  # Left
        ]

        # Recalibrate positions
        self._borders_info = [(self._calculate_position_info(*p1), (self._calculate_position_info(*p2)))
                              for p1, p2 in self._calculate_borders()]
        self._wheel_info = {}
        self._sensor_info = {}
        for wheel in self.wheels:
            self._wheel_info[wheel] = self._calculate_position_info(wheel.x, wheel.y)
            wheel.x, wheel.y = self._calculate_position(*self._wheel_info[wheel])
        for sensor in self.sensors:
            self._sensor_info[sensor] = self._calculate_position_info(sensor.x, sensor.y)
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

    def pos(self):
        return self.x, self.y

    def speed(self):
        return self.wheels[0].speed + self.wheels[1].speed

    def set_speed(self, speed: float):
        half = speed / 2
        self._set_speed_helper(self.wheels[0], half)
        self._set_speed_helper(self.wheels[1], half)

    def change_speed(self, change: float):
        half = change / 2
        self._set_speed_helper(self.wheels[0], self.wheels[0].speed + half)
        self._set_speed_helper(self.wheels[1], self.wheels[1].speed + half)

    def reset(self):
        self.theta = math.radians(90)
        self.set_speed(0)
        self._recalculate_parts()

    def borders(self):
        # Returns the borders' positions relative to the vehicle's current position and angle
        return [(self._calculate_position(angle1, distance1), self._calculate_position(angle2, distance2))
                for (angle1, distance1), (angle2, distance2) in self._borders_info]

    def collides(self, line: tuple[tuple[float, float], tuple[float, float]]):
        for line2 in self.borders():
            if intersection := utils.intersects(line2, line):
                return intersection[0], intersection[1]
        return None

    def _recalculate_parts(self):
        # Move wheels
        for i, wheel in enumerate(self.wheels):
            wheel.x, wheel.y = self._calculate_position(*self._wheel_info[wheel])
        # Move sensors
        for i, sensor in enumerate(self.sensors):
            sensor.x, sensor.y = self._calculate_position(*self._sensor_info[sensor])

    def _calculate_position(self, angle: float, distance: float):
        """
        Calculates the position of a point relative to the center of the vehicle, given an angle and distance.

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

    def _calculate_position_info(self, x: float, y: float):
        """
        Calculates some location information of the given point RELATIVE to the center of the vehicle.
        This is intended to be used ONLY ONCE during initialisation.

        Returns
        -------
        tuple
            The angle (in radians) and distance of the part from the center.
        """
        angle = math.atan2(y - self.y, x - self.x)
        distance = utils.distance_2p((self.x, self.y), (x, y))
        return angle, distance

    def _calculate_borders(self):
        x, y = self.x - self.width / 2, self.y - self.height / 2
        return utils.calculate_borders((x, y), self.width, self.height)

    def _set_speed_helper(self, wheel: Wheel, speed: float):
        sign = math.copysign(1, speed)
        new_speed = min(enums.VEHICLE_MAXSPEED / 2, abs(speed))
        wheel.speed = sign * new_speed


@dataclass
class VehicleData:
    vehicle: Vehicle
    intersections: list[tuple[float, float, float]]
    collision: tuple | None = None
    displacement_start: float = 0.0
    displacement_goal: float = 0.0
    is_finished: bool = False
    start_time: float = 0.0
    time_taken: float = 0.0
    genome: list[float] = field(default=lambda: [])

    def reset(self):
        self.collision = None
        self.displacement_start = 0.0
        self.displacement_goal = 0.0
        self.is_finished = False
        self.start_time = 0.0
        self.time_taken = 0.0

    def as_dict(self):
        return asdict(self)

    def fitness_data(self):
        return self.displacement_start, self.displacement_goal, self.is_finished, self.time_taken

    def __repr__(self):
        return repr((self.displacement_start, self.displacement_goal, self.is_finished, self.time_taken))
