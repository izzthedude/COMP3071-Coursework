from project.agent import NavigatorAgent
from project.enums import *
from project.map_gen import MapGenerator, MapTile
from project.models import Vehicle
from project.utils import distance_2p


class Environment:
    def __init__(self):
        size = 7
        self.mapgen = MapGenerator(CANVAS_SIZE // size, size)

        start_x, start_y = self._calculate_vehicle_start()
        self.vehicle = Vehicle(start_x, start_y, VEHICLE_SIZE, VEHICLE_SIZE, 90)
        self.manual_dspeed_rate = 0.1
        self.manual_turn_dangle = 1

        self.agent: NavigatorAgent = NavigatorAgent(self.vehicle, 150)
        self.is_manual: bool = False

        self.collision = None
        self.intersections: dict = {}
        self._find_sensor_intersections()

    def tick(self):
        # Find collision and intersection points
        self.collision = None
        self._find_sensor_intersections()

        # Determine speed and direction using agent
        if not self.is_manual:
            inputs = [distance for _, _, distance in self.intersections.values()]
            dangle, dspeed = self.agent.determine(inputs)
            self.vehicle.theta += dangle
            self.vehicle.change_speed(dspeed)

        # Move vehicle and recreate canvas
        self.vehicle.move()

    def on_size_changed(self, value: int):
        self.mapgen.set_map_size(value)
        self.mapgen.set_tile_size(CANVAS_SIZE / value)

    def on_reset(self):
        self.vehicle.x, self.vehicle.y = self._calculate_vehicle_start()
        self.vehicle.reset()
        self._find_sensor_intersections()

    def on_regenerate(self):
        self.mapgen.regenerate()
        self.on_reset()

    def on_dspeed_changed(self, value: float):
        self.manual_dspeed_rate = value

    def on_turn_multiplier_changed(self, value: float):
        self.manual_turn_dangle = value

    def on_manual_mode_changed(self, state: bool):
        self.is_manual = bool(state)

    def _calculate_vehicle_start(self):
        first_tile = self.mapgen.get_tiles()[0]
        x = first_tile.x + (first_tile.size / 2)
        y = VEHICLE_SIZE / 2 + 5
        return x, y

    def _closest_tiles(self):
        def distance(tile: MapTile):
            tile_center = tile.x + (tile.size / 2), tile.y + (tile.size / 2)
            return distance_2p(tile_center, (self.vehicle.x, self.vehicle.y))

        tiles = self.mapgen.get_tiles()
        closest = sorted(tiles, key=distance)
        return closest

    def _find_sensor_intersections(self):
        tiles = self._closest_tiles()
        for i, sensor in enumerate(self.vehicle.sensors):
            first_intersected = False
            for j, tile in enumerate(tiles):
                if first_intersected:
                    break
                for k, border in enumerate(tile.borders):
                    if border is not None:
                        if not self.collision:
                            self.collision = self.vehicle.collides(border)

                        if tile_intersects := sensor.intersects(border, self.vehicle.theta):
                            self.intersections[sensor] = tile_intersects
                            first_intersected = True
                            break
                        else:
                            self.intersections[sensor] = (*sensor.line_end(self.vehicle.theta), sensor.sense_length)