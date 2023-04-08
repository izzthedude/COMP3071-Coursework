import math

from project.types import *


def distance_2p(p1: Point, p2: Point) -> float:
    """
    Calculates the distance between two points.
    Referenced from: https://www.mathwarehouse.com/algebra/distance_formula/index.php
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx ** 2 + dy ** 2)


def point_on_circle(origin: Point, radius: float, theta: float) -> Point:
    """
    Calculates a point on the circle's circumference.
    Referenced from: https://en.wikipedia.org/wiki/Circle#Equations
    """
    x = origin[0] + radius * math.cos(theta)
    y = origin[1] + radius * math.sin(theta)
    return x, y


def intersects(line1: Line, line2: Line) -> Point | None:
    """
    Calculates the intersection point between two lines.
    Referenced from https://gist.github.com/kylemcdonald/6132fc1c29fd3767691442ba4bc84018
    """
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2

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
    return x, y


def calculate_borders(top_left: Point, width: float, height: float) -> list[Line]:
    """
    Calculates the borders lines of a square/rectangle with the given top left point. The returned list of lines
    is in the order: TOP, RIGHT, BOTTOM, LEFT.
    """
    x, y = top_left
    borders = [
        ((x, y), (x + width, y)),  # Top
        ((x + width, y), (x + width, y + height)),  # Right
        ((x, y + height), (x + width, y + height)),  # Bottom
        ((x, y), (x, y + height))  # Left
    ]
    return borders


def average(values: list[int | float]) -> float:
    """
    Calculates the average of values in the given list
    """
    return sum(values) / len(values)


def change_cutoff(value: float, change: float, minimum: float, maximum: float) -> float:
    """
    Applies the change to the value. If the resulting value is below the minimum or above the maximum, the minimum or
    maximum value is returned instead.
    """
    new = value + change
    new = max(minimum, new)
    new = min(new, maximum)
    return new


def squash(value: float, domain: tuple[float, float]) -> float:
    """
    'Squashes' the given value into the given domain. The value is assumed to be between 0 and 1. The domain is a tuple
    of (lower boundary, upper boundary) values.
    """
    return (value * (domain[1] - domain[0])) + min(domain)
