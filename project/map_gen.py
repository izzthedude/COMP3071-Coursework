import random
from enum import Enum, auto

SIZE: int = 11


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    DOWN = auto()


def _within_range(num: int):
    return 0 <= num < SIZE


def _within_ranges(x: int, y: int):
    return _within_range(x) and _within_range(y)


def _print_arr(arr):
    for row in arr:
        print(row)


def _new_direction(new: Direction, x: int, y: int) -> tuple[int, int]:
    new_x = x
    new_y = y
    if new == Direction.LEFT:
        new_x -= 1
    elif new == Direction.RIGHT:
        new_x += 1
    else:
        new_y += 1

    return new_x, new_y


def _any_ends(arr: list):
    return any(arr[10]) or any([row[0] for row in arr]) or any([row[10] for row in arr])


def generate_map() -> list:
    array = [[0 for _ in range(SIZE)] for __ in range(SIZE)]
    array[0][SIZE // 2] = 1

    x = SIZE // 2
    y = 1
    current_direction = Direction.DOWN
    while _within_ranges(x, y) and not _any_ends(array):
        array[y][x] = 1

        direction_choices = [Direction.LEFT, Direction.RIGHT, Direction.DOWN]
        if current_direction == Direction.LEFT:
            direction_choices.remove(Direction.RIGHT)
        elif current_direction == Direction.RIGHT:
            direction_choices.remove(Direction.LEFT)

        new_direction = random.choice(direction_choices)
        new_x, new_y = _new_direction(new_direction, x, y)
        if new_direction != Direction.DOWN and _within_ranges(new_x, new_y + 1) and array[y - 1][new_x]:
            new_y += 1
            array[new_y][x] = 1

        current_direction = new_direction
        x = new_x
        y = new_y

    return array


if __name__ == '__main__':
    env = generate_map()
    _print_arr(env)
