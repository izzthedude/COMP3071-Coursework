import math
import random

import numpy as np

from project import enums
from project.models import VehicleData
from project.types import *


class NavigatorAgent:
    def __init__(self):
        # Topology
        self.input_size: int = 6
        self.num_hlayers: int = 2
        self.num_hneurons: int = 5
        self.output_size: int = 2

        # Weights
        self.weights: list[np.ndarray] = [
            0.1 * np.random.randn(self.input_size, self.num_hneurons),  # Input to first hidden layer
            *[0.1 * np.random.randn(self.num_hneurons, self.num_hneurons) for _ in range(self.num_hlayers - 1)],
            0.1 * np.random.randn(self.num_hneurons, self.output_size)  # Last hidden layer to output
        ]

    def predict(self, inputs: np.ndarray | list) -> tuple[float, float]:
        # Return adjusted output
        dtheta, dspeed = self._forward(inputs)
        return dtheta * math.radians(enums.VEHICLE_DANGLE), dspeed * enums.VEHICLE_DSPEED

    def _forward(self, inputs: np.ndarray | list) -> np.ndarray | list:
        # Input to first hidden layer
        houtputs = np.dot(inputs, self.weights[0])
        hactivations = relu(houtputs)
        self._hidden_activations = [hactivations]

        # Iterate through all hidden layers
        for i in range(1, self.num_hlayers):
            houtputs = np.dot(hactivations, self.weights[i])
            hactivations = relu(houtputs)
            self._hidden_activations.append(hactivations)

        # Output layer
        last_outputs = np.dot(hactivations, self.weights[-1])
        last_activations = np.tanh(last_outputs)  # Outputs are between -1 and 1
        return last_activations

    def to_genome(self) -> Genome:
        # Flatten the weights into one big list of weights
        flattened = []
        for layer in self.weights:
            flattened += layer.flatten().tolist()
        return flattened

    def from_genome(self, genome: Genome):
        # Convert a list of weights to the weights of this neural network with the correct topology
        last_index = 0

        inputs_to_hidden = []
        for i in range(0, self.input_size):
            start = i * self.num_hneurons
            end = start + self.num_hneurons
            inputs_to_hidden.append(genome[start:end])
            last_index = end

        hidden_to_hidden = []
        for i in range(0, self.num_hlayers - 1):
            layer = []
            for j in range(0, self.num_hneurons):
                start = last_index
                end = start + self.num_hneurons
                layer.append(genome[start:end])
                last_index = end
            hidden_to_hidden.append(layer)

        hidden_to_output = []
        for i in range(0, self.num_hneurons):
            start = last_index
            end = start + self.output_size
            hidden_to_output.append(genome[start:end])
            last_index = end

        return [
            np.array(inputs_to_hidden),  # Inputs to hidden
            *[np.array(layer) for layer in hidden_to_hidden],  # Hidden to hidden
            np.array(hidden_to_output)  # Hidden to output
        ]


class GeneticAlgorithm:
    @staticmethod
    def fitness(data: VehicleData) -> float:
        # The fitness will be the ratio between displacement from start and displacement from goal
        ratio = math.sqrt(data.displacement_start) / math.sqrt(data.displacement_goal)
        out = ratio

        # If the vehicle has reached its goal, the number of ticks it took to reach there also factors in
        if data.is_finished:
            ticks_taken = data.end_tick - data.start_tick
            # Values here are arbitrary. Adjust them to change how much the time should influence the fitness
            # You can visualise this function over at https://www.desmos.com/calculator
            multiplier = 15  # HIGHER = more influence
            power = 0.5  # LOWER = more influence
            offset = -1  # HIGHER = more influence
            out = exp_decay(ticks_taken * 0.10, multiplier, power, offset) + ratio

        return out

    @staticmethod
    def selection_pair(population: Population, fitnesses: list[float]) -> tuple[Genome, Genome]:
        if not sum(fitnesses):  # If weights are all zero
            return random.choices(population=population, k=2)

        return random.choices(
            population=population,
            weights=fitnesses,
            k=2
        )

    @staticmethod
    def crossover(genome1: Genome, genome2: Genome) -> tuple[Genome, Genome]:
        length = len(genome1)
        if length != len(genome2):
            raise ValueError(f"Length of given gnomes are not equal. {length} != {len(genome2)}")

        if length < 2:
            return genome1, genome2

        # Crossover at random index
        index = random.randint(1, length - 1)
        return genome1[0:index] + genome2[index:], genome2[0:index] + genome1[index:]

    @staticmethod
    def mutation(genome: Genome, mutation_chance: float, mutation_rate: float) -> Genome:
        mutated = genome.copy()  # Avoid modifying given genome

        for i in range(len(genome)):
            if random.random() < mutation_chance:
                mutated[i] += random.choice([-1, 1]) * mutation_rate
                if random.random() < mutation_rate:  # Chance to flip the sign of the gene
                    mutated[i] *= -1

        return mutated

    @staticmethod
    def next_generation(population: Population, datas: tuple[VehicleData], carry_over: float,
                        mutation_chance: float, mutation_rate: float) -> Population:
        # Sort population by fitness
        fitnesses = [GeneticAlgorithm.fitness(data) for data in datas]
        sorted_population = sorted(
            enumerate(population),
            key=lambda enum: fitnesses[enum[0]],
            reverse=True
        )
        sorted_population = [pop for i, pop in sorted_population]

        # Carry over the top carry_over% of the population
        num = int(len(sorted_population) * carry_over)
        next_generation: Population = sorted_population[:num]
        while len(next_generation) < len(population):
            parents = GeneticAlgorithm.selection_pair(population, fitnesses)
            child_a, child_b = GeneticAlgorithm.crossover(*parents)
            child_a = GeneticAlgorithm.mutation(child_a, mutation_chance, mutation_rate)
            child_b = GeneticAlgorithm.mutation(child_b, mutation_chance, mutation_rate)
            next_generation += [child_a, child_b]

        # For odd population sizes
        if len(next_generation) > len(population):
            next_generation = next_generation[:-1]

        return next_generation


def relu(inputs: np.ndarray) -> np.ndarray:
    # Rectified Linear Unit
    return np.maximum(0, inputs)


def exp_decay(value: float, multiplier: float, power: float, offset: float):
    # Exponentially increase output as the input approaches 0
    return (multiplier / (value ** power)) + offset
