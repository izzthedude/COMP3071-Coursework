import math


class Wheel:
    def __init__(self, x: float, y: float, width: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = self.width / 3
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
            return x, y, self._distance_from_start(x, y)

    def _distance_from_start(self, x: int, y: int):
        startx, starty = self.line_start()
        dx = startx - x
        dy = starty - y

        if dx == 0:
            result = dy
        elif dy == 0:
            result = dx
        else:
            angle = math.atan(dy / dx)
            result = dx / math.sin(angle)

        return abs(result)

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
        wheel_width = self.width / 2
        self.wheels: list[Wheel] = [
            Wheel(self.x, self.y - self.height / 2, wheel_width),
            Wheel(self.x, self.y + self.height / 2, wheel_width)
        ]
        self.wheels[0].speed = 2
        self.wheels[1].speed = 1.8

        # Sensors
        sensor_x = self.x + self.width / 2
        sensor_size = self.width / 6
        sense_angle = math.radians(45)
        self.sensors: list[Sensor] = [
            Sensor(sensor_x, (self.y + (self.height / 2)) * 0.25, sensor_size, -sense_angle),
            Sensor(sensor_x, (self.y + (self.height / 2)) * 0.50, sensor_size, 0),
            Sensor(sensor_x, (self.y + (self.height / 2)) * 0.75, sensor_size, sense_angle)
        ]

        # Recalibrate positions
        self._wheel_info = {}
        self._sensor_info = {}
        for wheel in self.wheels:
            self._wheel_info[wheel] = self._calculate_wheel_info(wheel)
            wheel.x, wheel.y = self._calculate_position(*self._wheel_info[wheel])
        for sensor in self.sensors:
            self._sensor_info[sensor] = self._calculate_sensor_info(sensor)
            sensor.x, sensor.y = self._calculate_position(*self._sensor_info[sensor])

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
        newx = self.x + distance * math.cos(self.theta - angle)
        newy = self.y + distance * math.sin(self.theta - angle)
        return newx, newy

    def _calculate_wheel_info(self, wheel: Wheel):
        """
        Calculates some location information of wheel RELATIVE to the center of the vehicle.
        This is intended to be used ONCE during initialisation.

        Returns
        -------
        tuple
            The angle (in radians) and distance of the wheel from the center.
        """
        length = self.width / 2
        angle = 2 * (math.atan((self.y - wheel.y) / length))
        return angle, length

    def _calculate_sensor_info(self, sensor: Sensor):
        """
        Calculates some location information of sensor RELATIVE to the center of the vehicle.
        This is intended to be used ONCE during initialisation.

        Returns
        -------
        tuple
            The angle (in radians) and distance of the sensor from the center.
        """
        angle = math.atan((self.y - sensor.y) / (self.width / 2))
        sin = math.sin(angle)
        distance = self.width / 2
        if sin:
            distance = (self.y - sensor.y) / sin

        return angle, distance
