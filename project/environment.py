import math
import os
import pickle
import random
from datetime import datetime

from project import enums
from project import utils
from project.agent import NavigatorAgent, GeneticAlgorithm as GA
from project.map_gen import MapGenerator, MapTile, Direction
from project.models import Vehicle, VehicleData


class Environment:
    def __init__(self):
        # Environment parameters
        self.tick_interval = 20
        self.ticks_per_gen = 750
        self.auto_reset: bool = True
        self.regen_n_runs_enabled: bool = False
        self.regen_n_runs: int = 4
        self.resize_n_regens_enabled: bool = False
        self.resize_n_regens: int = 6
        self.learning_mode: bool = True
        self.dynamic_mutation: bool = True
        self.mutation_chance_domain = (0.01, 0.40)  # Domains here are mainly for dynamic mutation use. Not UI.
        self.mutation_rate_domain = (0.01, 0.20)
        self.mutation_chance: float = self.mutation_chance_domain[1]
        self.mutation_rate: float = 0.05

        self.current_ticks = 0
        self.current_map_run: int = 0
        self.current_mapsize_run: int = 0
        self.initial_regen_runs = self.regen_n_runs
        self.carryover_percentage = 0.20
        self.current_best_vehicle: Vehicle | None = None

        self.generation: int = 0
        self.first_successful_generation: int | None = None
        self.num_successful_agents: int = 0

        # Map
        map_size = 3
        self.mapgen = MapGenerator(enums.CANVAS_SIZE // map_size, map_size)

        # Initialise vehicles
        x, y = self._calculate_vehicle_start()
        vehicles = (Vehicle(x, y, enums.VEHICLE_SIZE, enums.VEHICLE_SIZE, 90) for _ in range(enums.NUM_POPULATION))

        # Initialise vehicles' agents and datas
        self.vehicles: dict[Vehicle, tuple[NavigatorAgent, VehicleData]] = {
            vehicle: (NavigatorAgent(), VehicleData(*self._find_sensor_intersections(vehicle)))
            for vehicle in vehicles
        }

    def tick(self):
        self.current_ticks += 1

        # Iterate through vehicles and do a bunch of calculations
        last_tile = self.mapgen.tiles()[-1]
        for vehicle, (agent, data) in self.vehicles.items():

            # Only calculate for vehicles that haven't collided or finished
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
                    data.ticks_taken = self.current_ticks

                    self.num_successful_agents += 1
                    if not self.first_successful_generation:
                        self.first_successful_generation = self.generation

                inputs = [distance for (_, _), distance in data.intersections] + [vehicle.speed()]
                dtheta, dspeed = agent.predict(inputs)
                vehicle.theta += dtheta
                vehicle.change_speed(dspeed)

        # Get current best fit vehicle
        all_ticks = [data.ticks_taken for data in self.vehicle_datas()]
        fitness: list[tuple[Vehicle, float]] = [(vehicle, GA.fitness(data, all_ticks))
                                                for vehicle, (_, data) in self.vehicles.items()]
        fitness.sort(key=lambda pair: pair[1], reverse=True)
        self.current_best_vehicle = fitness[0][0]

        # Check if current run is done
        ticks_finished = self.current_ticks >= self.ticks_per_gen
        all_collided_or_finished = all(data.collision or data.is_finished for data in self.vehicle_datas())
        done = ticks_finished or all_collided_or_finished
        if done:
            self.end_current_run()

        return done

    def end_current_run(self, reset: bool = False, proceed_nextgen: bool = False):
        if self.regen_n_runs_enabled:
            # Update current map run if haven't reached limit
            if self.current_map_run + 1 < self.regen_n_runs:
                self.current_map_run += 1

            # Regenerate current map if current_map_run >= regen_n_runs
            else:
                if self.resize_n_regens_enabled:
                    # Update current map size run if haven't reached limit
                    if self.current_mapsize_run + 1 < self.resize_n_regens:
                        self.current_mapsize_run += 1

                    # Resize map once reached limit
                    else:
                        if self.learning_mode:
                            # Increment map size by one
                            new_size = self.get_map_size() + 1
                            if new_size > 11:
                                new_size = 3

                        else:
                            new_size = random.randint(3, 11)

                        self.on_size_changed(new_size)
                        self.current_mapsize_run = 0

                self.current_map_run = 0
                self.mapgen.regenerate()

        # If success
        if any(data.is_finished for data in self.vehicle_datas()):
            pass
        else:
            self.current_map_run = 0
            self.current_mapsize_run = 0

        # Auto reset
        if self.auto_reset or reset:
            if self.learning_mode or proceed_nextgen:
                self.on_generation_end()
            self.on_reset()

    def on_generation_end(self):
        # Get next generation
        population = [agent.to_genome() for agent in self.vehicle_agents()]
        datas = self.vehicle_datas()
        next_generation = GA.next_generation(
            population, datas,
            self.carryover_percentage,
            self.mutation_chance,
            self.mutation_rate)

        all_ticks = [data.ticks_taken for data in datas]
        fitted_datas = sorted(datas, key=lambda data: GA.fitness(data, all_ticks), reverse=True)

        # Apply next generation to agents
        for agent, genome in zip(self.vehicle_agents(), next_generation):
            agent.weights = agent.from_genome(genome)

        # Adjust chance of mutation if dynamic mutation is True
        if self.dynamic_mutation:
            num = math.ceil(len(fitted_datas) * self.carryover_percentage)
            top = fitted_datas[:num]
            avg_fitness = utils.average([GA.fitness(data, all_ticks) for data in top])
            adjusted = math.tanh(1 / avg_fitness) if avg_fitness else self.mutation_chance_domain[1]
            self.mutation_chance = utils.squash(adjusted, self.mutation_chance_domain)

        self.generation += 1

    def on_reset(self):
        self.current_ticks = 0
        self.num_successful_agents = 0

        for vehicle, (_, data) in self.vehicles.items():
            vehicle.x, vehicle.y = self._calculate_vehicle_start()
            vehicle.reset()
            data.reset()
            self._calculate_vehicle_data(vehicle)

    def on_regenerate(self):
        self.current_mapsize_run = 0
        self.current_map_run = 0
        self.mapgen.regenerate()
        self.on_reset()

    def on_size_changed(self, value: int):
        change = value - self.get_map_size()
        size = int(utils.change_cutoff(self.get_map_size(), change, 3, 11))
        self.mapgen.set_map_size(size)
        self.mapgen.set_tile_size(enums.CANVAS_SIZE / size)

    def on_save_best_agent(self, directory: str):
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        file_name = datetime.now().strftime("agent_%Y%m%d_%H%M%S.pickle")
        file_path = os.path.join(directory, file_name)
        with open(file_path, "wb") as file:
            agent = self.vehicle_agent(self.current_best_vehicle)
            pickle.dump(agent, file)

    def on_load_agent(self, path: str):
        with open(path, "rb") as file:
            new_agent = pickle.load(file)

            # Replace first vehicle's agent with the new loaded agent
            vehicle = self.get_vehicles()[0]
            data = self.vehicle_data(vehicle)
            data.is_custom_agent = True
            self.vehicles[vehicle] = (new_agent, data)

    def set_learning_mode(self, enabled: bool):
        self.auto_reset = enabled
        self.learning_mode = enabled
        self.regen_n_runs_enabled = enabled
        self.resize_n_regens_enabled = enabled
        self.dynamic_mutation = enabled
        self.regen_n_runs = 2
        self.resize_n_regens = 10

    def get_map_size(self):
        return self.mapgen.map_size()

    def get_vehicles(self):
        return tuple(vehicle for vehicle in self.vehicles.keys())

    def vehicle_agent(self, vehicle: Vehicle):
        return self.vehicles[vehicle][0]

    def vehicle_agents(self):
        return tuple(agent for agent, _ in self.vehicles.values())

    def vehicle_data(self, vehicle: Vehicle):
        return self.vehicles[vehicle][1]

    def vehicle_datas(self):
        return tuple(data for _, data in self.vehicles.values())

    def _calculate_vehicle_start(self):
        first_tile = self.mapgen.tiles()[0]
        x = first_tile.x + (first_tile.size / 2)
        y = enums.VEHICLE_SIZE / 2 + 10
        return x, y

    def _closest_tiles(self, vehicle: Vehicle):
        def distance(tile: MapTile):
            tile_center = tile.x + (tile.size / 2), tile.y + (tile.size / 2)
            return utils.distance_2p(tile_center, (vehicle.x, vehicle.y))

        return sorted(self.mapgen.tiles(), key=distance)

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
                            intersections[sensor] = (sensor.end(vehicle.theta), enums.SENSOR_LENGTH)

        return list(intersections.values()), collision

    def _calculate_vehicle_data(self, vehicle: Vehicle):
        data = self.vehicle_data(vehicle)
        data.intersections, data.collision = self._find_sensor_intersections(vehicle)
        data.displacement_start = utils.distance_2p(self._calculate_vehicle_start(), vehicle.pos())
        data.displacement_goal = utils.distance_2p(self.mapgen.tiles()[-1].center(), vehicle.pos())
