import math

from project.models import Vehicle


class NavigatorAgent:
    def __init__(self, vehicle: Vehicle, threshold: int):
        self._vehicle = vehicle
        self._threshold = threshold
        self._sensor_directions = [-1, 0, 1, 1, -1]

    def determine(self, inputs: list[float]) -> tuple[float, float]:
        lspeed = 1
        rspeed = 1

        front_center = inputs[1]
        center_change = 0
        if front_center < self._threshold / 2:
            center_change = -(self._vehicle.max_speed / front_center) * 6

        distance_dirs = zip(self._sensor_directions, inputs)
        horizontal_sum = sum([direction * _weighted(distance) for direction, distance in distance_dirs if direction])

        lspeed += center_change - horizontal_sum
        rspeed += center_change + horizontal_sum
        return lspeed, rspeed


def _weighted(distance: float):
    return math.e ** (15 / abs(distance)) - 1
