import random
from enum import Enum


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
    def __init__(self, size: float, x: float, y: float, from_direction: Direction, to_direction: Direction):
        self.size = size
        self.x = x * size
        self.y = y * size
        self.from_direction = from_direction
        self.to_direction = to_direction

        self.borders: list[tuple[tuple[float, float], tuple[float, float]] | None] = []

    def top_border(self):
        return self.borders[0]

    def bottom_border(self):
        return self.borders[1]

    def left_border(self):
        return self.borders[2]

    def right_border(self):
        return self.borders[3]

    def _calculate_borders(self):
        top = self._calculate_border((self.x, self.y), (self.x + self.size, self.y), Direction.UP)
        self.borders.append(top)
        bottom = self._calculate_border((self.x, self.y + self.size), (self.x + self.size, self.y + self.size),
                                        Direction.DOWN)
        self.borders.append(bottom)
        left = self._calculate_border((self.x, self.y), (self.x, self.y + self.size), Direction.LEFT)
        self.borders.append(left)
        right = self._calculate_border((self.x + self.size, self.y), (self.x + self.size, self.y + self.size),
                                       Direction.RIGHT)
        self.borders.append(right)

    def _calculate_border(self, start: tuple[float, float], end: tuple[float, float], direction: Direction):
        border = start, end
        if self.from_direction == direction or self.to_direction == direction:
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
    def __init__(self, tile_size: float, map_size: int = 7):
        self._map_size: int = map_size
        self._tile_size: float = tile_size
        self._map: list[list[int | MapTile]] = []
        self._tiles: list[MapTile] = []
        self.regenerate()

    def set_size(self, size: int):
        self._map_size = size

    def get_size(self) -> int:
        return self._map_size

    def get_map(self) -> list:
        return self._map

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
