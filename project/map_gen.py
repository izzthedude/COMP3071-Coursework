import random
from enum import Enum, auto

SIZE: int = 11


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    DOWN = auto()


def _within_range(num: int):
    return 0 <= num < SIZE


def _print_arr(arr):
    for row in arr:
        print(row)


def generate_map() -> list:
    array = [[0 for _ in range(SIZE)] for __ in range(SIZE)]
    array[0][SIZE // 2] = 1

    x_current = SIZE // 2
    y_current = 1
    current_direction = Direction.DOWN
    while _within_range(x_current) and _within_range(y_current):
        if any(array[10]) or any([row[0] for row in array]) or any([row[10] for row in array]):
            break
        array[y_current][x_current] = 1

        direction_choices = [Direction.LEFT, Direction.RIGHT, Direction.DOWN]
        if current_direction == Direction.LEFT:
            direction_choices.remove(Direction.RIGHT)
        elif current_direction == Direction.RIGHT:
            direction_choices.remove(Direction.LEFT)

        new_direction = random.choice(direction_choices)
        if new_direction == Direction.LEFT:
            if array[y_current - 1][x_current - 1]:
                array[y_current][x_current] = 1
                y_current += 1
            else:
                x_current -= 1

        elif new_direction == Direction.RIGHT and _within_range(x_current + 1):
            if array[y_current - 1][x_current + 1]:
                array[y_current][x_current] = 1
                y_current += 1
            else:
                x_current += 1

        else:
            y_current += 1

        current_direction = new_direction

    return array


if __name__ == '__main__':
    env = generate_map()
    _print_arr(env)
