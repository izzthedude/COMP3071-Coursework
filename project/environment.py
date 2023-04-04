from dataclasses import dataclass

from project.agent import NavigatorAgent
from project.enums import *
from project.map_gen import MapGenerator, MapTile
from project.models import Vehicle
from project.utils import distance_2p


@dataclass
class VehicleData:
    collision: tuple | None
    intersections: list[tuple[float, float, float]]

    def set_values(self, collision: tuple | None, intersections: list[tuple[float, float, float]]):
        self.collision = collision
        self.intersections = intersections


class Environment:
    def __init__(self):
        size = 7
        self.mapgen = MapGenerator(CANVAS_SIZE // size, size)

        start_x, start_y = self._calculate_vehicle_start()
        vehicles = [Vehicle(start_x, start_y, VEHICLE_SIZE, VEHICLE_SIZE, 90) for _ in range(NUM_POPULATION)]
        self.vehicles: dict[Vehicle, VehicleData] = {
            vehicle: VehicleData(*self._find_sensor_intersections(vehicle)) for vehicle in vehicles
        }
        self.agents: dict[Vehicle, NavigatorAgent] = {vehicle: NavigatorAgent(vehicle, 100) for vehicle in vehicles}

    def tick(self):
        # If all cars have collided, reset the environment
        if all(data.collision for data in self.vehicles.values()):
            self.on_reset()

        for vehicle, data in self.vehicles.items():
            if not data.collision:
                # Find collision and intersection points
                collision, intersections = self._find_sensor_intersections(vehicle)
                data.set_values(collision, intersections)

                # Move vehicle
                vehicle.move()

    def on_size_changed(self, value: int):
        self.mapgen.set_map_size(value)
        self.mapgen.set_tile_size(CANVAS_SIZE / value)

    def on_reset(self):
        for vehicle, data in self.vehicles.items():
            vehicle.x, vehicle.y = self._calculate_vehicle_start()
            vehicle.reset()
            data.set_values(*self._find_sensor_intersections(vehicle))

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
        collision = None
        intersections = {}
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

        return collision, list(intersections.values())
