import csv
import json
import math
import os
import pickle
from datetime import datetime

from project import enums
from project import utils
from project.agent import NavigatorAgent, GeneticAlgorithm as GA
from project.map_gen import MapGenerator, MapTile, Direction
from project.models import Vehicle, VehicleData


class Environment:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
    AGENTS_DIR = os.path.join(PROJECT_ROOT, "agents")
    EXPERIMENTS_DIR = os.path.join(PROJECT_ROOT, "experiments")

    def __init__(self):
        # Environment parameters
        self.tick_interval: int = 20
        self.ticks_per_gen: int = 750
        self.auto_reset: bool = True
        self.regen_n_runs_enabled: bool = False
        self.regen_n_runs: int = 4
        self.resize_n_regens_enabled: bool = False
        self.resize_n_regens: int = 6
        self.learning_mode: bool = True
        self.dynamic_mutation: bool = True
        self.mutation_chance_domain: tuple[float, float] = (0.01, 0.40)  # Domains here are mainly for dynamic
        self.mutation_rate_domain: tuple[float, float] = (0.01, 0.20)  # mutation use. Not UI.
        self.mutation_chance: float = self.mutation_chance_domain[1]
        self.mutation_rate: float = 0.05
        self.carryover_percentage: float = 0.20

        self.current_ticks: int = 0
        self.current_map_run: int = 0
        self.current_mapsize_run: int = 0
        self.current_best_vehicle: Vehicle | None = None
        self.generation: int = 0

        self.loaded_agent: str = ""
        self.run_reports: list[dict] = []
        self.experiment_results: dict = {}

        # Map
        map_size: int = 3
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

                # Use agent to predict vehicle movement
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
            if not self.learning_mode:
                self.run_reports.append(self.report_current_run())
            self.end_current_run()

    def end_current_run(self, reset: bool = False, proceed_nextgen: bool = False):
        if self.regen_n_runs_enabled:
            # Update current map run if haven't reached limit
            if self.current_map_run + 1 < self.regen_n_runs:
                self.current_map_run += 1

            # Regenerate current map if current_map_run >= regen_n_runs
            else:
                self.current_map_run = 0

                if self.resize_n_regens_enabled:
                    # Update current map size run if haven't reached limit
                    if self.current_mapsize_run + 1 < self.resize_n_regens:
                        self.current_mapsize_run += 1

                    # Resize map once reached limit
                    else:
                        self.current_mapsize_run = 0

                        # Increment map size by one
                        new_size = self.get_map_size() + 1
                        if new_size > 11:  # This also signifies the completion of a learning process or experiment
                            new_size = 3

                            # TODO (low): Somehow stop the simulation once it loops back
                            if self.learning_mode:
                                self.save_best_agent(Environment.AGENTS_DIR)
                                self.learning_mode = False
                            else:
                                self.compile_reports()
                                self.save_experiment(self.EXPERIMENTS_DIR)
                                self.run_reports.clear()
                                self.experiment_results.clear()

                        self.change_map_size(new_size)

                self.mapgen.regenerate()

        # If success
        if any(data.is_finished for data in self.vehicle_datas()):
            pass
        elif self.learning_mode:
            self.current_map_run = 0
            self.current_mapsize_run = 0

        # Auto reset
        if self.auto_reset or reset:
            if self.learning_mode or proceed_nextgen:
                self.proceed_next_generation()
            self.reset_vehicles()

    def proceed_next_generation(self):
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

    def reset_vehicles(self):
        self.current_ticks = 0

        for vehicle, (_, data) in self.vehicles.items():
            vehicle.x, vehicle.y = self._calculate_vehicle_start()
            vehicle.reset()
            data.reset()
            self._calculate_vehicle_data(vehicle)

    def regenerate_map(self):
        self.current_mapsize_run = 0
        self.current_map_run = 0
        self.mapgen.regenerate()
        self.reset_vehicles()

    def change_map_size(self, value: int):
        change = value - self.get_map_size()
        size = int(utils.change_cutoff(self.get_map_size(), change, 3, 11))
        self.mapgen.set_map_size(size)
        self.mapgen.set_tile_size(enums.CANVAS_SIZE / size)

    def save_best_agent(self, directory: str):
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        current = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_names = [
            f"agent_{current}.pickle",  # Best fit agent only
            f"agent_{current}_avg.pickle"  # Average of some best fit agents
        ]

        file_paths = [os.path.join(directory, file_name) for file_name in file_names]
        for file_path in file_paths:
            with open(file_path, "wb") as file:
                if "_avg" in file_path:
                    agent = self._average_best_weights()
                else:
                    agent = self.vehicle_agent(self.current_best_vehicle)

                pickle.dump(agent, file)

    def load_agent(self, path: str):
        with open(path, "rb") as file:
            new_agent = pickle.load(file)

            # Replace first vehicle's agent with the new loaded agent
            vehicle = self.get_vehicles()[0]
            data = self.vehicle_data(vehicle)
            data.is_custom_agent = True
            self.vehicles[vehicle] = (new_agent, data)

        self.loaded_agent = path

    def report_current_run(self) -> dict:
        vehicle = self.get_vehicles()[0]
        data = self.vehicle_data(vehicle)

        collided = bool(data.collision)
        return {
            "map_size": self.get_map_size(),
            "collided": collided,
            "ticks_taken": data.ticks_taken
        }

    def compile_reports(self):
        self.experiment_results = {
            "agent": self.loaded_agent,
            "total_collisions": 0,
            "total_runs": len(self.run_reports),
            "runs_per_size": self.resize_n_regens
        }
        sizes = []

        for report in self.run_reports:
            self.experiment_results["total_collisions"] += int(report["collided"])
            size = report['map_size']
            sizes.append(size)
            self.experiment_results[f"map{size}"] = {}

        for size in sizes:
            key = f"map{size}"
            maps = tuple(filter(lambda report: report["map_size"] == size, self.run_reports))
            collisions = sum([int(report["collided"]) for report in maps])
            avg_ticks = utils.average([report["ticks_taken"] for report in maps])

            self.experiment_results[key]["runs"] = len(maps)
            self.experiment_results[key]["collisions"] = collisions
            self.experiment_results[key]["average_ticks"] = avg_ticks

    def save_experiment(self, directory: str):
        current = datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment_dir = os.path.join(directory, f"exp_{current}")
        if not os.path.exists(experiment_dir):
            os.makedirs(experiment_dir, exist_ok=True)

        run_reports_path = os.path.join(experiment_dir, "run_reports.json")
        with open(run_reports_path, "w") as file:
            json.dump(self.run_reports, file)

        exp_results_path = os.path.join(experiment_dir, "experiment_results.json")
        with open(exp_results_path, "w") as file:
            json.dump(self.experiment_results, file)

        self._convert_experiment_to_csv(self.experiment_results, experiment_dir)

    def set_learning_mode(self, enabled: bool):
        self.learning_mode = enabled
        if enabled:
            self.auto_reset = enabled
            self.regen_n_runs_enabled = enabled
            self.resize_n_regens_enabled = enabled
            self.dynamic_mutation = enabled
            self.regen_n_runs = 3
            self.resize_n_regens = 12
        else:
            self.regen_n_runs = 1
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

    def _average_best_weights(self) -> NavigatorAgent:
        all_ticks = [data.ticks_taken for data in self.vehicle_datas()]
        best_fits: list[tuple[Vehicle, float]] = [(vehicle, GA.fitness(data, all_ticks))
                                                  for vehicle, (_, data) in self.vehicles.items()]
        best_fits.sort(key=lambda pair: pair[1], reverse=True)

        num = math.ceil(len(self.vehicles) * self.carryover_percentage)
        best_agents: list[NavigatorAgent] = [self.vehicle_agent(vehicle) for vehicle, _ in best_fits][:num]

        avg_agent: NavigatorAgent = NavigatorAgent()
        for layer in range(len(avg_agent.weights)):
            for row in range(len(avg_agent.weights[layer])):
                for weight in range(len(avg_agent.weights[layer][row])):
                    avg_weights = utils.average([agent.weights[layer][row][weight] for agent in best_agents])
                    avg_agent.weights[layer][row][weight] = avg_weights

        return avg_agent

    def _convert_experiment_to_csv(self, experiment: dict, directory: str):
        map_keys = tuple(filter(lambda key: key.startswith("map"), experiment.keys()))
        map_sizes = [int(key[3:]) for key in map_keys]
        collisions = [experiment[key]["collisions"] for key in map_keys]
        avg_ticks = [experiment[key]["average_ticks"] for key in map_keys]
        collisions_csv = [("Map Sizes", "Collisions")] + list(zip(map_sizes, collisions))
        avg_ticks_csv = [("Map Sizes", "Average Ticks")] + list(zip(map_sizes, avg_ticks))

        collisions_path = os.path.join(directory, "collisions.csv")
        avg_ticks_path = os.path.join(directory, "avg_ticks.csv")
        self._write_csv(collisions_path, collisions_csv)
        self._write_csv(avg_ticks_path, avg_ticks_csv)

    def _write_csv(self, path: str, data: list):
        with open(path, "w") as file:
            writer = csv.writer(file, delimiter=" ")
            writer.writerows(data)
