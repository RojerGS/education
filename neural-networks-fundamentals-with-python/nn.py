import math
import numpy as np
from abc import ABC, abstractmethod


def create_weight_matrix(nrows, ncols):
    """Create a weight matrix with normally distributed random elements."""
    return np.random.normal(loc=0, scale=1/(nrows*ncols), size=(nrows, ncols))

def create_bias_vector(length):
    """Create a bias vector with normally distributed random elements."""
    return np.random.normal(loc=0, scale=1/length, size=(length, 1))


class ActivationFunction:
    """Class to be inherited by activation functions."""
    @abstractmethod
    def f(self, x):
        """The method that implements the function."""
        pass

    @abstractmethod
    def df(self, x):
        """Derivative of the function with respect to its input."""
        pass

class Id(ActivationFunction):
    def f(self, x):
        return x

    def df(self, x):
        return np.ones(x.shape)

class ELU(ActivationFunction):
    """Exponential Linear Unit."""
    def __init__(self, alpha=0.1):
        self.alpha = alpha

    def f(self, x):
        out = self.alpha*(np.exp(x) - 1)
        out[x > 0] = x[x > 0]
        return out

    def df(self, x):
        return np.maximum(x >= 0, self.alpha*(x < 0)*np.exp(x))

class LeakyReLU(ActivationFunction):
    """Leaky Rectified Linear Unit."""
    def __init__(self, leaky_param=0.1):
        self.alpha = leaky_param

    def f(self, x):
        return np.maximum(x, x*self.alpha)

    def df(self, x):
        return np.maximum(x > 0, self.alpha)

class ReLU(LeakyReLU):
    """Leaky ReLU with parameter 0."""
    def __init__(self):
        super().__init__(0)

class Sigmoid(ActivationFunction):
    def f(self, x):
        return 1/(1 + np.exp(-x))

    def df(self, x):
        return self.f(x) * (1 - self.f(x))

class Tanh(ActivationFunction):
    def f(self, x):
        return np.tanh(x)

    def df(self, x):
        return 1 - self.f(x)**2

class ArcTan(ActivationFunction):
    def f(self, x):
        return np.arctan(x)

    def df(self, x):
        return 1/(1 + x**2)


class LossFunction:
    """Class to be inherited by loss functions."""
    @abstractmethod
    def loss(self, values, expected):
        """Compute the loss of the computed values with respect to the expected ones."""
        pass

    @abstractmethod
    def dloss(self, values, expected):
        """Derivative of the loss with respect to the computed values."""
        pass

class MSELoss(LossFunction):
    """Mean Squared Error Loss function."""
    def loss(self, values, expected):
        return np.mean((values - expected)**2)

    def dloss(self, values, expected):
        return 2*(values - expected)/values.size

class CrossEntropyLoss(LossFunction):
    def loss(self, values, expected):
        return -values[expected, 0] + math.log(np.sum(np.exp(values)))

    def dloss(self, values, expected):
        d = np.exp(values)/np.sum(np.exp(values))
        d[expected, 0] -= 1
        return d


class Layer:
    """Model the connections between two sets of neurons in a network."""
    def __init__(self, ins, outs, act_function):
        self.ins = ins
        self.outs = outs
        self.act_function = act_function

        self._W = create_weight_matrix(self.outs, self.ins)
        self._b = create_bias_vector(self.outs)

    def forward_pass(self, x):
        """Compute the next set of neuron states with the given set of states."""
        return self.act_function.f(np.dot(self._W, x) + self._b)


class NeuralNetwork:
    """A series of connected, compatible layers."""
    def __init__(self, layers, loss_function, learning_rate):
        self._layers = layers
        self._loss_function = loss_function
        self.lr = learning_rate

        # Check layer compatibility
        for (from_, to_) in zip(self._layers[:-1], self._layers[1:]):
            if from_.outs != to_.ins:
                raise ValueError("Layers should have compatible shapes.")

    def forward_pass(self, x):
        out = x
        for layer in self._layers:
            out = layer.forward_pass(out)
        return out

    def loss(self, values, expected):
        return self._loss_function.loss(values, expected)

    def train(self, x, t):
        """Train the network on input x and expected output t."""

        # Accumulate intermediate results during forward pass.
        xs = [x]
        for layer in self._layers:
            xs.append(layer.forward_pass(xs[-1]))

        dx = self._loss_function.dloss(xs.pop(), t)
        for layer, x in zip(self._layers[::-1], xs[::-1]):
            # Compute the derivatives
            y = np.dot(layer._W, x) + layer._b
            db = layer.act_function.df(y) * dx
            dx = np.dot(layer._W.T, db)
            dW = np.dot(db, x.T)
            # Update parameters.
            layer._W -= self.lr * dW
            layer._b -= self.lr * db
