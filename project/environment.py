import math
import random
import time

from project import enums
from project import utils
from project.agent import NavigatorAgent, GeneticAlgorithm as GA
from project.map_gen import MapGenerator, MapTile, Direction
from project.models import Vehicle, VehicleData


class Environment:
    def __init__(self):
        # Environment parameters
        self.tick_interval = 20
        self.ticks_per_gen = 700
        self.current_ticks = 0
        self.auto_reset: bool = True
        self.learning_mode: bool = True
        self.regen_on_success: int = 5
        self.current_map_success: int = 0
        self.resize_on_success: int = 3
        self.current_mapsize_success: int = 0
        self.dynamic_mutation: bool = True
        self.mutation_chance_domain = (0.01, 0.40)
        self.mutation_rate_domain = (0.05, 0.20)
        self.mutation_chance: float = self.mutation_chance_domain[1]
        self.mutation_rate: float = self.mutation_rate_domain[0]
        self.carryover_percentage = 0.20
        self._is_first_tick: bool = True

        # Generation info
        self.generation: int = 0
        self.first_successful_generation: int | None = None
        self.num_successful_agents: int = 0

        # Map
        map_size = 7
        self.mapgen = MapGenerator(enums.CANVAS_SIZE // map_size, map_size)

        # Initialise vehicles
        start_x, start_y = self._calculate_vehicle_start()
        self.vehicles = [Vehicle(start_x, start_y, enums.VEHICLE_SIZE, enums.VEHICLE_SIZE, 90)
                         for _ in range(enums.NUM_POPULATION)]

        # Initialise vehicles' agents and datas
        self.agents: dict[Vehicle, NavigatorAgent] = {vehicle: NavigatorAgent() for vehicle in self.vehicles}
        self.datas: dict[Vehicle, VehicleData] = {
            vehicle: VehicleData(*self._find_sensor_intersections(vehicle))
            for vehicle in self.vehicles}

    def tick(self):
        self.current_ticks += 1

        last_tile = self.mapgen.get_tiles()[-1]
        for vehicle in self.vehicles:
            data = self.datas[vehicle]
            if self._is_first_tick:
                data.start_time = time.time()

            # Only calculate for a vehicle that hasn't collided or finished
            if not (data.collision or data.is_finished):
                vehicle.move()
                self._calculate_vehicle_data(vehicle)

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

                    self.num_successful_agents += 1
                    if not self.first_successful_generation:
                        self.first_successful_generation = self.generation

                inputs = [distance for _, _, distance in data.intersections] + [vehicle.speed()]
                dtheta, dspeed = self.agents[vehicle].predict(inputs)
                vehicle.theta += dtheta
                vehicle.change_speed(dspeed)

        if self._is_first_tick:
            self._is_first_tick = False

        ticks_finished = self.current_ticks >= self.ticks_per_gen
        all_collided_or_finished = all(data.collision or data.is_finished for data in self.datas.values())
        done = ticks_finished or all_collided_or_finished

        if done:
            self.end_current_run()

        return done

    def end_current_run(self, reset: bool = False, proceed_nextgen: bool = False):
        # If success
        if any(data.is_finished for data in self.datas.values()):
            # Check for current map success
            if self.current_map_success + 1 < self.regen_on_success:
                self.current_map_success += 1
            elif self.regen_on_success > 0:
                self.mapgen.regenerate()
                self.current_map_success = 0

                # Check for current map SIZE success
                if self.current_mapsize_success + 1 < self.resize_on_success:
                    self.current_mapsize_success += 1

                elif self.resize_on_success > 0:
                    self.on_size_changed(random.randint(3, 11))
                    self.mapgen.regenerate()
                    self.current_mapsize_success = 0
                    self.current_map_success = 0

        # If no success
        else:
            self.current_mapsize_success = 0
            self.current_map_success = 0

        if self.auto_reset or reset:
            if self.learning_mode or proceed_nextgen:
                self.on_generation_end()
            self.on_reset()

    def on_generation_end(self):
        population = [self.agents[vehicle].to_genome() for vehicle in self.vehicles]
        datas = [self.datas[vehicle] for vehicle in self.vehicles]
        next_generation = GA.next_generation(
            population, datas,
            self.carryover_percentage,
            self.mutation_chance,
            self.mutation_rate)
        fitted_datas = sorted(datas, key=lambda data: GA.fitness(data), reverse=True)

        for vehicle, genome in zip(self.vehicles, next_generation):
            agent = self.agents[vehicle]
            agent.weights = agent.from_genome(genome)

        if self.dynamic_mutation:
            num = int(len(fitted_datas) * self.carryover_percentage)
            top = fitted_datas[:num]
            avg_fitness = utils.average([GA.fitness(data) for data in top])

            self.mutation_chance = utils.squash(math.tanh(1 / avg_fitness), self.mutation_chance_domain)

        self.generation += 1

    def on_reset(self):
        self._is_first_tick = True
        self.current_ticks = 0
        self.num_successful_agents = 0

        for vehicle, data in self.datas.items():
            vehicle.x, vehicle.y = self._calculate_vehicle_start()
            vehicle.reset()
            data.reset()
            self._calculate_vehicle_data(vehicle)

    def on_regenerate(self):
        self.current_mapsize_success = 0
        self.current_map_success = 0
        self.mapgen.regenerate()
        self.on_reset()

    def on_size_changed(self, value: int):
        self.mapgen.set_map_size(value)
        self.mapgen.set_tile_size(enums.CANVAS_SIZE / value)

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
            return utils.distance_2p(tile_center, (vehicle.x, vehicle.y))

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

    def _calculate_vehicle_data(self, vehicle: Vehicle):
        data = self.datas[vehicle]
        data.intersections, data.collision = self._find_sensor_intersections(vehicle)
        data.displacement_start = utils.distance_2p(self._calculate_vehicle_start(), vehicle.pos())
        data.displacement_goal = utils.distance_2p(self.mapgen.get_tiles()[-1].center(), vehicle.pos())

    def _change_mutation_rate(self, change: float):
        self.mutation_rate = utils.change_cutoff(
            self.mutation_rate,
            change,
            *self.mutation_rate_domain
        )
