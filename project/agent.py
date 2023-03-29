import json

import numpy as np


class NavigatorAgent:
    def __init__(self, n_inputs: int, n_hlayers: int, n_hneurons: int, n_outputs: int):
        self._input_size = n_inputs
        self._num_hlayers = n_hlayers
        self._num_hneurons = n_hneurons
        self._output_size = n_outputs
        self._total_layers = n_hlayers + 2

        self.weights = [
            np.random.randn(n_inputs, n_hneurons),  # Input to first hidden layer
            *[np.random.randn(n_hneurons, n_hneurons) for _ in range(n_hlayers)],  # Hidden layers
            np.random.randn(n_hneurons, n_outputs)  # Last hidden layer to output
        ]
        self.biases = [
            np.zeros((1, n_hneurons)),  # Input layer
            *[np.zeros((1, n_hneurons)) for _ in range(n_hlayers)],  # Hidden layers
            np.zeros((1, n_outputs))  # Output layer
        ]

    @classmethod
    def load(cls, path: str):
        with open(path, "r") as file:
            data = json.load(file)

        agent = cls(
            data["n_inputs"],
            data["n_hlayers"],
            data["n_hneurons"],
            data["n_outputs"]
        )
        agent.weights = data["weights"]
        agent.biases = data["biases"]
        return agent

    def save(self, path: str):
        data = {
            "n_inputs": self._input_size,
            "n_hlayers": self._num_hlayers,
            "n_hneurons": self._num_hneurons,
            "n_outputs": self._output_size,
            "weights": [w.tolist() for w in self.weights],
            "biases": [b.tolist() for b in self.biases]
        }
        with open(path, "w") as file:
            json.dump(data, file)

    def update(self, path: str, weight: float = 0.1):
        with open(path, "r") as file:
            data = json.load(file)

        if "weights" in data:
            for i in range(self._total_layers):
                self.weights[i] = ((1.0 - weight) * self.weights[i]) + (weight * np.array(data["weights"]))
        if "biases" in data:
            for i in range(self._total_layers):
                self.biases[i] = (self.biases[i] * (1.0 - weight)) + (weight * np.array(data["biases"]))

    def predict(self, inputs: np.ndarray | list) -> np.ndarray:
        output = self._forward(inputs)
        return output

    def train(self, inputs: np.ndarray | list, expected: np.ndarray, learning_rate: float = 0.1,
              epochs: int = 100) -> list:
        losses = []
        for i in range(epochs):
            predicted = self.predict(inputs)
            loss = _mse(predicted, expected)
            losses.append(float(loss))
            self._backward(inputs, predicted, expected, learning_rate)

        return losses

    def _forward(self, inputs: np.ndarray | list) -> np.ndarray:
        # Input to first hidden layer
        houtputs = _layer_out(inputs, self.weights[0], self.biases[0])
        hactivations = _relu(houtputs)
        self._hidden_activations = [hactivations]

        # Iterate through all hidden layers
        for i in range(1, self._num_hlayers + 1):
            houtputs = _layer_out(hactivations, self.weights[i], self.biases[i])
            hactivations = _relu(houtputs)
            self._hidden_activations.append(hactivations)

        # Output layer
        last_outputs = _layer_out(hactivations, self.weights[-1], self.biases[-1])
        return last_outputs

    def _backward(self, inputs: np.ndarray | list, output_predicted: np.ndarray, output_expected: np.ndarray,
                  learning_rate: float):

        # Sanitise inputs and make sure it's the right type and shape
        inputs_sanitised = inputs[:]
        if not isinstance(inputs_sanitised, np.ndarray):
            inputs_sanitised = np.array(inputs)
        if inputs_sanitised.shape != (self._input_size, 1):
            inputs_sanitised.reshape((self._input_size, 1))

        # Calculate delta/gradient for output
        delta = (output_expected - output_predicted) * _sigmoid_derivative(output_predicted)
        for i in range(self._total_layers - 1, -1, -1):
            if i == 0:
                layer = inputs_sanitised
            else:
                layer = self._hidden_activations[i - 1]

            self.weights[i] += learning_rate * np.dot(layer.T, delta)
            self.biases[i] += learning_rate * np.sum(delta, axis=0, keepdims=True)
            delta = np.dot(delta, self.weights[i].T) * (layer > 0)


def squash(value: float, domain: tuple[float, float]) -> float:
    multiplier, offset = _squash_helper(domain)
    return (value - offset) / multiplier


def desquash(value: float, domain: tuple[float, float]) -> float:
    multiplier, offset = _squash_helper(domain)
    return (value * multiplier) + offset


def _squash_helper(domain: tuple[float, float]):
    return abs(domain[1] - domain[0]), min(domain)


def _layer_out(inputs: np.ndarray | list, lweight: np.ndarray, lbias: np.ndarray) -> np.ndarray:
    return np.dot(inputs, lweight) + lbias


def _relu(inputs: np.ndarray) -> np.ndarray:
    # Rectified Linear Unit
    return np.maximum(0, inputs)


def _relu_derivative(inputs: np.ndarray) -> np.ndarray:
    return np.where(
        inputs > 0,  # condition
        1,  # if condition is True
        0)  # else


def _sigmoid(inputs: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-inputs))


def _sigmoid_derivative(inputs: np.ndarray) -> np.ndarray:
    # NOTE: it's assumed that 'inputs' here are the outputs of the agent.
    # So 'inputs' must already be 'sigmoided'
    return inputs * (1 - inputs)


def _mse(output_predicted: np.ndarray, output_actual: np.ndarray) -> np.float64:
    # Mean Square Error
    return np.sum((output_actual - output_predicted) ** 2) / output_predicted.size


def _mse_gradient(output_predicted: np.ndarray, output_actual: np.ndarray):
    return 2 * (output_actual - output_predicted) / output_predicted.size


if __name__ == '__main__':
    # Dummy data
    sensors = np.array([[85, 91, 23, 103, 55]])
    expected = np.array([0.4, 0.6, 0.1])
    agent = NavigatorAgent(5, 2, 10, 3)
    output = agent.predict(sensors)
    print(output)
    agent.train(sensors, expected)
