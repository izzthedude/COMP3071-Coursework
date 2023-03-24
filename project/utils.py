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
