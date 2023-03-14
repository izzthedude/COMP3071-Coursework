import random
from enum import Enum, auto


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    DOWN = auto()


class MapGenerator:
    def __init__(self, size: int = 11):
        self._size: int = size
        self._map: list = []
        self.regenerate()

    def set_size(self, size: int):
        self._size = size

    def get_map(self) -> list:
        return self._map

    def regenerate(self) -> list:
        self._map = self._generate_map(self._new_map())
        return self._map

    def _generate_map(self, array: list):
        new_arr = array[0:]
        x = self._size // 2
        y = 1
        current_direction = Direction.DOWN
        while self._within_ranges(x, y) and not self._any_ends(new_arr):
            new_arr[y][x] = 1

            direction_choices = [Direction.LEFT, Direction.RIGHT, Direction.DOWN]
            if current_direction == Direction.LEFT:
                direction_choices.remove(Direction.RIGHT)
            elif current_direction == Direction.RIGHT:
                direction_choices.remove(Direction.LEFT)

            new_direction = random.choice(direction_choices)
            new_x, new_y = self._new_directions(new_direction, x, y)
            if new_direction != Direction.DOWN and self._within_ranges(new_x, new_y + 1) and new_arr[y - 1][new_x]:
                new_y += 1
                new_arr[new_y][x] = 1

            current_direction = new_direction
            x = new_x
            y = new_y

        return new_arr

    def _new_directions(self, new: Direction, x: int, y: int) -> tuple[int, int]:
        new_x = x
        new_y = y
        if new == Direction.LEFT:
            new_x -= 1
        elif new == Direction.RIGHT:
            new_x += 1
        else:
            new_y += 1

        return new_x, new_y

    def _new_map(self):
        array = [[0 for _ in range(self._size)] for __ in range(self._size)]
        array[0][self._size // 2] = 1
        return array

    def _any_ends(self, array: list) -> bool:
        return any(array[self._size - 1]) or \
            any([row[0] for row in array]) or \
            any([row[self._size - 1] for row in array])

    def _within_range(self, num: int) -> bool:
        return 0 <= num < self._size

    def _within_ranges(self, x: int, y: int) -> bool:
        return self._within_range(x) and self._within_range(y)

    def __repr__(self):
        return "\n".join([f"{row}" for row in self._map])


if __name__ == '__main__':
    gen = MapGenerator(11)
    print(gen)
