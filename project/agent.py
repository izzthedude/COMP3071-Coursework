import math
import random

import numpy as np

from project.models import Vehicle


def _relu(inputs: np.ndarray) -> np.ndarray:
    # Rectified Linear Unit
    return np.maximum(0, inputs)


def _sigmoid(inputs: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-inputs))


def _squash(value: float, domain: tuple[float, float]) -> float:
    multiplier, offset = _squash_helper(domain)
    return (value - offset) / multiplier


def _desquash(value: float, domain: tuple[float, float]) -> float:
    multiplier, offset = _squash_helper(domain)
    return (value * multiplier) + offset


def _squash_helper(domain: tuple[float, float]):
    return abs(domain[1] - domain[0]), min(domain)


class NavigatorAgent:
    def __init__(self, vehicle: Vehicle):
        self._vehicle = vehicle
        self._dtheta_domain = (math.radians(-5), math.radians(5))
        self._dspeed_domain = (-1, 1)

        self.input_size = 6
        self.num_hlayers = 2
        self.num_hneurons = 10
        self.output_size = 2
        self._total_layers = self.num_hlayers + 2

        self.weights: list[np.ndarray] = [
            0.1 * np.random.randn(self.input_size, self.num_hneurons),  # Input to first hidden layer
            *[0.1 * np.random.randn(self.num_hneurons, self.num_hneurons) for _ in range(self.num_hlayers - 1)],
            0.1 * np.random.randn(self.num_hneurons, self.output_size)  # Last hidden layer to output
        ]

    def predict(self, inputs: np.ndarray | list) -> tuple[float, float]:
        out_dtheta, out_dspeed = self._forward(inputs)
        return _desquash(out_dtheta, self._dtheta_domain), _desquash(out_dspeed, self._dspeed_domain)

    def _forward(self, inputs: np.ndarray | list) -> np.ndarray:
        # Input to first hidden layer
        houtputs = np.dot(inputs, self.weights[0])
        hactivations = _relu(houtputs)
        self._hidden_activations = [hactivations]

        # Iterate through all hidden layers
        for i in range(1, self.num_hlayers):
            houtputs = np.dot(hactivations, self.weights[i])
            hactivations = _relu(houtputs)
            self._hidden_activations.append(hactivations)

        # Output layer
        last_outputs = np.dot(hactivations, self.weights[-1])
        last_activations = _sigmoid(last_outputs)
        return last_activations


class GeneticAlgorithm:
    @staticmethod
    def selection_pair(population: list[list[float]], distances: list[float]):
        return random.choices(
            population=population,
            weights=[distance for distance in sorted(distances, key=lambda distance: distance, reverse=True)],
            k=2
        )

    @staticmethod
    def crossover(genome1: list[float], genome2: list[float]):
        length = len(genome1)
        if length != len(genome2):
            raise ValueError(f"Length of given gnomes are not equal. {length} != {len(genome2)}")

        if length < 2:
            return genome1, genome2

        index = random.randint(1, length - 1)
        return genome1[0:index] + genome2[index:], genome2[0:index] + genome1[index:]

    @staticmethod
    def mutation(genome: list[float], num: int = 5, mutation_rate: float = 0.2):
        mutated = genome.copy()
        for _ in range(num):
            if random.random() > 0.5:
                index = random.randrange(len(genome))
                sign = random.choice([-1, 1])
                mutated[index] += sign * mutation_rate
        return mutated

    @staticmethod
    def next_generation(population: list[list[float]], distances: list[float],
                        num_mutation: int = 10, mutation_rate: float = 0.5):
        # Sort by longest distance/vector travelled from the starting point
        zipped_sorted = sorted(zip(population, distances), key=lambda item: item[1], reverse=True)
        population = [pop for pop, distance in zipped_sorted]
        next_generation = population[:2]
        for i in range(len(population) // 2 - 1):
            parents = GeneticAlgorithm.selection_pair(population, distances)
            child_a, child_b = GeneticAlgorithm.crossover(*parents)
            child_a = GeneticAlgorithm.mutation(child_a, num_mutation, mutation_rate)
            child_b = GeneticAlgorithm.mutation(child_b, num_mutation, mutation_rate)
            next_generation += [child_a, child_b]

        return next_generation

    @staticmethod
    def weights_to_genome(nn: NavigatorAgent):
        flattened = []
        for layer in nn.weights:
            flattened += layer.flatten().tolist()
        return flattened

    @staticmethod
    def genome_to_weights(nn: NavigatorAgent, genome: list):
        last_index = 0
        inputs_to_hidden = []
        for i in range(0, nn.input_size):
            start = i * nn.num_hneurons
            end = start + nn.num_hneurons
            inputs_to_hidden.append(genome[start:end])
            last_index = end

        hidden_to_hidden = []
        for i in range(0, nn.num_hlayers - 1):
            layer = []
            for j in range(0, nn.num_hneurons):
                start = last_index
                end = start + nn.num_hneurons
                layer.append(genome[start:end])
                last_index = end
            hidden_to_hidden.append(layer)

        hidden_to_output = []
        for i in range(0, nn.num_hneurons):
            start = last_index
            end = start + nn.output_size
            hidden_to_output.append(genome[start:end])
            last_index = end

        return [
            np.array(inputs_to_hidden),  # Inputs to hidden
            *[np.array(layer) for layer in hidden_to_hidden],  # Hidden to hidden
            np.array(hidden_to_output)  # Hidden to output
        ]
