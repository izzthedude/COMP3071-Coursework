import random
from enum import Enum

from project import utils
from project.types import *


class Direction(Enum):
    LEFT = "L"
    RIGHT = "R"
    DOWN = "D"
    UP = "U"

    def opposite(self):
        match self:
            case Direction.LEFT:
                return Direction.RIGHT
            case Direction.RIGHT:
                return Direction.LEFT
            case Direction.UP:
                return Direction.DOWN
            case Direction.DOWN:
                return Direction.UP


class MapTile:
    def __init__(self, size: int, x: int, y: int, from_direction: Direction, to_direction: Direction):
        self.size = size
        self.x = x * size
        self.y = y * size
        self.from_direction = from_direction
        self.to_direction = to_direction

        # self._borders is for borders info without considering whether it should be drawn or not
        self._borders: list[Line] = []
        self.borders: list[Line | None] = []

    def finish_line(self):
        match self.to_direction:
            case Direction.RIGHT | Direction.LEFT:
                p1 = self.x + self.size / 2, self.y
                p2 = self.x + self.size / 2, self.y + self.size
                return p1, p2

            case Direction.DOWN:
                p1 = self.x, self.y + self.size / 2
                p2 = self.x + self.size, self.y + self.size / 2
                return p1, p2

    def pos(self):
        return self.x, self.y

    def center(self):
        return self.x + self.size / 2, self.y + self.size / 2

    def top_border(self):
        return self._borders[0]

    def right_border(self):
        return self._borders[1]

    def bottom_border(self):
        return self._borders[2]

    def left_border(self):
        return self._borders[3]

    def _calculate_borders(self):
        self._borders = utils.calculate_borders((self.x, self.y), self.size, self.size)

        self.borders = self._borders.copy()
        self.borders[0] = self._determine_border(self._borders[0], Direction.UP)
        self.borders[1] = self._determine_border(self._borders[1], Direction.RIGHT)
        self.borders[2] = self._determine_border(self._borders[2], Direction.DOWN)
        self.borders[3] = self._determine_border(self._borders[3], Direction.LEFT)

    def _determine_border(self, line: Line, direction: Direction):
        border = line
        if direction in [self.from_direction, self.to_direction]:
            border = None
        return border

    def __eq__(self, other):
        return self.x == other.x and \
            self.y == other.y and \
            self.from_direction == other.from_direction and \
            self.to_direction == other.to_direction

    def __repr__(self):
        return f"({self.from_direction.value},{self.to_direction.value})"


class MapGenerator:
    def __init__(self, tile_size: int, map_size: int = 7):
        self._map_size: int = map_size
        self._tile_size: int = tile_size
        self._map: list[list[int | MapTile]] = []
        self._tiles: list[MapTile] = []
        self.regenerate()

    def set_map_size(self, size: int):
        self._map_size = size

    def get_map_size(self) -> int:
        return self._map_size

    def get_map(self) -> list:
        return self._map

    def set_tile_size(self, size: float):
        self._tile_size = size

    def get_tiles(self) -> list[MapTile]:
        return self._tiles

    def regenerate(self) -> list:
        self._map = self._generate_map()
        return self._map

    def _generate_map(self):
        new_arr: list[list[int | MapTile]] = self._new_map()
        x = self._map_size // 2
        y = 1
        to_direction: Direction = Direction.DOWN
        from_direction: Direction = to_direction
        while self._within_ranges(x, y) and not self._any_ends(new_arr):
            direction_choices = [Direction.LEFT, Direction.RIGHT, Direction.DOWN]
            if from_direction == Direction.LEFT:
                direction_choices.remove(Direction.RIGHT)
            elif from_direction == Direction.RIGHT:
                direction_choices.remove(Direction.LEFT)
            to_direction = random.choice(direction_choices)

            tile = MapTile(self._tile_size, x, y, from_direction.opposite(), to_direction)
            new_arr[y][x] = tile
            self._tiles.append(tile)

            new_x, new_y = self._new_directions(to_direction, x, y)
            if to_direction != Direction.DOWN and self._within_ranges(new_x, new_y + 1) and new_arr[y - 1][new_x]:
                new_y += 1
                new_arr[y][x] = MapTile(self._tile_size, x, y, Direction.UP, Direction.DOWN)
                new_arr[new_y][x] = MapTile(self._tile_size, x, new_y, Direction.UP, to_direction)
                self._tiles.remove(self._tiles[-1])
                self._tiles.append(new_arr[y][x])
                self._tiles.append(new_arr[new_y][x])

            from_direction = to_direction
            x = new_x
            y = new_y

        self._tiles[-1].to_direction = self._tiles[-1].from_direction.opposite()
        for tile in self._tiles:
            tile._calculate_borders()

        first = self._tiles[0]
        first.borders[0] = first.top_border()

        last = self._tiles[-1]
        match last.to_direction:
            case Direction.RIGHT:
                last.borders[1] = last.right_border()
            case Direction.DOWN:
                last.borders[2] = last.bottom_border()
            case Direction.LEFT:
                last.borders[3] = last.left_border()

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
        size = self._tile_size
        first = MapTile(size, self._map_size // 2, 0, Direction.UP, Direction.DOWN)
        array = [[0 for _ in range(self._map_size)] for __ in range(self._map_size)]
        array[0][self._map_size // 2] = first
        self._tiles = []
        self._tiles.append(first)
        return array

    def _any_ends(self, array: list) -> bool:
        return any(array[self._map_size - 1]) or \
            any([row[0] for row in array]) or \
            any([row[-1] for row in array])

    def _within_range(self, num: int) -> bool:
        return 0 <= num < self._map_size

    def _within_ranges(self, x: int, y: int) -> bool:
        return self._within_range(x) and self._within_range(y)

    def __repr__(self):
        return "\n".join([" | ".join([f"{str(item):^5}" for item in row]) for row in self._map])


if __name__ == '__main__':
    gen = MapGenerator(11)
    print(gen)
