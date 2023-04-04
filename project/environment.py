from dataclasses import dataclass

from project.enums import *
from project.map_gen import MapGenerator, MapTile, Direction
from project.models import Vehicle
from project.utils import distance_2p


@dataclass
class VehicleData:
    intersections: list[tuple[float, float, float]]
    collision: tuple | None = None
    distance: float = 0
    is_finished: bool = False

    def set_values(self, collision: tuple | None, intersections: list[tuple[float, float, float]]):
        self.collision = collision
        self.intersections = intersections


class Environment:
    def __init__(self):
        size = 7
        self.mapgen = MapGenerator(CANVAS_SIZE // size, size)

        start_x, start_y = self._calculate_vehicle_start()
        self.vehicles = [Vehicle(start_x, start_y, VEHICLE_SIZE, VEHICLE_SIZE, 90) for _ in range(NUM_POPULATION)]
        self.vehicle_datas: dict[Vehicle, VehicleData] = {
            vehicle: VehicleData(*self._find_sensor_intersections(vehicle)) for vehicle in self.vehicles
        }

        self._all_collided: bool = False
        self._any_finished: bool = False

    def tick(self):
        self._any_finished = any(data.is_finished for data in self.vehicle_datas.values())
        self._all_collided = all(data.collision for data in self.vehicle_datas.values())
        if self._any_finished or self._all_collided:
            self.on_reset()

        first_tile = self.mapgen.get_tiles()[0]
        last_tile = self.mapgen.get_tiles()[-1]

        for vehicle in self.vehicles:
            data = self.vehicle_datas[vehicle]
            if not data.collision and not data.is_finished:  # Only calculate for a vehicle that hasn't collided and hasn't finished
                vehicle.move()

                data.intersections, data.collision = self._find_sensor_intersections(vehicle)
                data.distance = distance_2p(first_tile.pos(), vehicle.pos())

                # Check if past finish line
                (x1, y1), (x2, y2) = last_tile.finish_line()
                if last_tile.to_direction == Direction.RIGHT:
                    data.is_finished = vehicle.x >= x1 and y1 <= vehicle.y <= y2
                elif last_tile.to_direction == Direction.DOWN:
                    data.is_finished = vehicle.y >= y1 and x1 <= vehicle.x <= x2
                elif last_tile.to_direction == Direction.LEFT:
                    data.is_finished = vehicle.x <= x1 and y1 <= vehicle.y <= y2

    def on_size_changed(self, value: int):
        self.mapgen.set_map_size(value)
        self.mapgen.set_tile_size(CANVAS_SIZE / value)

    def on_reset(self):
        self._all_collided = False
        self._any_finished = False

        for vehicle, data in self.vehicle_datas.items():
            vehicle.x, vehicle.y = self._calculate_vehicle_start()
            vehicle.reset()
            data.intersections, data.collision = self._find_sensor_intersections(vehicle)
            data.is_finished = False

    def on_regenerate(self):
        self.mapgen.regenerate()
        self.on_reset()

    def _calculate_vehicle_start(self):
        first_tile = self.mapgen.get_tiles()[0]
        x = first_tile.x + (first_tile.size / 2)
        y = VEHICLE_SIZE / 2 + 5
        return x, y

    def _closest_tiles(self, vehicle: Vehicle):
        def distance(tile: MapTile):
            tile_center = tile.x + (tile.size / 2), tile.y + (tile.size / 2)
            return distance_2p(tile_center, (vehicle.x, vehicle.y))

        return sorted(self.mapgen.get_tiles(), key=distance)

    def _find_sensor_intersections(self, vehicle: Vehicle):
        intersections = {}
        collision = None
        tiles = self._closest_tiles(vehicle)
        for i, sensor in enumerate(vehicle.sensors):
            first_intersected = False
            for j, tile in enumerate(tiles):
                if first_intersected:
                    break
                for k, border in enumerate(tile.borders):
                    if border:
                        if not collision:
                            collision = vehicle.collides(border)

                        if tile_intersects := sensor.intersects(border, vehicle.theta):
                            intersections[sensor] = tile_intersects
                            first_intersected = True
                            break
                        else:
                            intersections[sensor] = (*sensor.line_end(vehicle.theta), sensor.sense_length)

        return list(intersections.values()), collision
