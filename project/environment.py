import time

from project import enums
from project.agent import NavigatorAgent, GeneticAlgorithm as GA
from project.map_gen import MapGenerator, MapTile, Direction
from project.models import Vehicle, VehicleData
from project.utils import distance_2p


class Environment:
    def __init__(self):
        size = 7
        self.mapgen = MapGenerator(enums.CANVAS_SIZE // size, size)

        start_x, start_y = self._calculate_vehicle_start()
        self.vehicles = [Vehicle(start_x, start_y, enums.VEHICLE_SIZE, enums.VEHICLE_SIZE, 90) for _ in
                         range(enums.NUM_POPULATION)]
        self.vehicle_datas: dict[Vehicle, VehicleData] = {
            vehicle: VehicleData(vehicle, *self._find_sensor_intersections(vehicle)) for vehicle in self.vehicles
        }
        self.vehicle_agents: dict[Vehicle, NavigatorAgent] = {
            vehicle: NavigatorAgent(vehicle) for vehicle in self.vehicles
        }

        self.auto_reset: bool = True
        self.learning_mode: bool = True

        self._first_tick: bool = True
        self.generation: int = 0

    def tick(self):
        last_tile = self.mapgen.get_tiles()[-1]
        for vehicle in self.vehicles:
            data = self.vehicle_datas[vehicle]
            if self._first_tick:
                data.start_time = time.time()

            # Only calculate for a vehicle that hasn't collided or finished
            if not (data.collision or data.is_finished):
                vehicle.move()

                data.intersections, data.collision = self._find_sensor_intersections(vehicle)
                data.displacement_start = distance_2p(self._calculate_vehicle_start(), vehicle.pos())
                data.displacement_goal = distance_2p(last_tile.center(), vehicle.pos())

                # Check if past finish line
                (x1, y1), (x2, y2) = last_tile.finish_line()
                if last_tile.to_direction == Direction.RIGHT:
                    data.is_finished = vehicle.x >= x1 and y1 <= vehicle.y <= y2
                elif last_tile.to_direction == Direction.DOWN:
                    data.is_finished = vehicle.y >= y1 and x1 <= vehicle.x <= x2
                elif last_tile.to_direction == Direction.LEFT:
                    data.is_finished = vehicle.x <= x1 and y1 <= vehicle.y <= y2

                if data.is_finished:
                    data.time_taken = time.time() - data.start_time

                inputs = [distance for _, _, distance in data.intersections] + [vehicle.speed()]
                dtheta, dspeed = self.vehicle_agents[vehicle].predict(inputs)
                vehicle.theta += dtheta
                vehicle.change_speed(dspeed)

        if self._first_tick:
            self._first_tick = False

        if all(data.collision or data.is_finished for data in self.vehicle_datas.values()):
            if self.learning_mode:
                self.on_generation_end()
            if self.auto_reset:
                self.on_reset()

    def on_generation_end(self):
        population = [GA.weights_to_genome(self.vehicle_agents[vehicle]) for vehicle in self.vehicles]
        datas = [self.vehicle_datas[vehicle] for vehicle in self.vehicles]
        for i in range(len(datas)):
            datas[i].genome = population[i]

        next_generation = GA.next_generation(datas)
        for vehicle, genome in zip(self.vehicles, next_generation):
            agent = self.vehicle_agents[vehicle]
            agent.weights = GA.genome_to_weights(agent, genome)

        self.generation += 1

    def on_size_changed(self, value: int):
        self.mapgen.set_map_size(value)
        self.mapgen.set_tile_size(enums.CANVAS_SIZE / value)

    def on_reset(self):
        self._first_tick = True

        for vehicle, data in self.vehicle_datas.items():
            vehicle.x, vehicle.y = self._calculate_vehicle_start()
            vehicle.reset()
            data.intersections, data.collision = self._find_sensor_intersections(vehicle)
            data.reset()

    def on_regenerate(self):
        self.mapgen.regenerate()
        self.on_reset()

    def on_save_best_model(self):
        pass

    def on_load_model(self, path: str):
        pass

    def _calculate_vehicle_start(self):
        first_tile = self.mapgen.get_tiles()[0]
        x = first_tile.x + (first_tile.size / 2)
        y = enums.VEHICLE_SIZE / 2 + 10
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

