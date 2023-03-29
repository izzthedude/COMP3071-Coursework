import math


def distance_2p(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """
    Calculates the distance between two points.

    Referenced from: https://www.mathwarehouse.com/algebra/distance_formula/index.php
    Parameters
    ----------
    p1
        The first x and y point
    p2
        The second x and y point

    Returns
    -------
    float
        The distance between the two given points.
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx ** 2 + dy ** 2)


def point_on_circle(origin: tuple[float, float], radius: float, theta: float) -> tuple[float, float]:
    """
    Calculates a point on the circle's circumference.

    Referenced from: https://en.wikipedia.org/wiki/Circle#Equations
    Parameters
    ----------
    origin
        The origin/center point of the circle
    radius
        The radius of the circle
    theta
        The angle (in radians) of where the point is located relative to 0.

    Returns
    -------
    tuple[float, float]
        A tuple of the x and y point.
    """
    x = origin[0] + radius * math.cos(theta)
    y = origin[1] + radius * math.sin(theta)
    return x, y


def intersects(line1: tuple[tuple[float, float], tuple[float, float]],
               line2: tuple[tuple[float, float], tuple[float, float]]
               ) -> tuple[float, float] | None:
    """
    Calculates the intersection point between two lines.

    Referenced from https://gist.github.com/kylemcdonald/6132fc1c29fd3767691442ba4bc84018
    Parameters
    ----------
    line1
        A tuple containing two points of the first line
    line2
        A tuple containing two points of the second line

    Returns
    -------
    tuple[float, float]
        A tuple of the x and y point where the two lines intersect.
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


def calculate_borders(top_left: tuple[float, float], width: float, height: float
                      ) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    x, y = top_left
    borders = [
        ((x, y), (x + width, y)),  # Top
        ((x + width, y), (x + width, y + height)),  # Right
        ((x, y + height), (x + width, y + height)),  # Bottom
        ((x, y), (x, y + height))  # Left
    ]
    return borders
