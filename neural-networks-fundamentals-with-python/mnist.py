from nn import ReLU, LeakyReLU, Sigmoid, CrossEntropyLoss, Layer, NeuralNetwork
import csv
import numpy as np

def load_data(filepath, delimiter=",", dtype=float):
    """Load a numerical numpy array from a file."""

    print(f"Loading {filepath}...")
    with open(filepath, "r") as f:
        data_iterator = csv.reader(f, delimiter=delimiter)
        data_list = list(data_iterator)
    data = np.asarray(data_list, dtype=dtype)
    print("Done.")
    return data

def to_col(vec):
    return vec.reshape((vec.size, 1))

def test(net, test_data):
    correct = 0
    for i, test_row in enumerate(test_data):
        if not i%1000:
            print(i)

        t = test_row[0]
        x = to_col(test_row[1:])
        out = net.forward_pass(x)
        guess = np.argmax(out)
        if t == guess:
            correct += 1

    return correct/test_data.shape[0]

def train(net, train_data):
    # # Precompute all target vectors.
    # ts = {}
    # for t in range(10):
    #     tv = np.zeros((10, 1))
    #     tv[t] = 1
    #     ts[t] = tv

    for i, train_row in enumerate(train_data):
        if not i%1000:
            print(i)

        t = train_row[0]
        x = to_col(train_row[1:])
        net.train(x, t)


if __name__ == "__main__":
    layers = [
        Layer(784, 16, LeakyReLU()),
        Layer(16, 16, LeakyReLU()),
        Layer(16, 10, Sigmoid()),
    ]
    net = NeuralNetwork(layers, CrossEntropyLoss(), 0.001)

    test_data = load_data("mnistdata/mnist_test.csv", delimiter=",", dtype=int)

    accuracy = test(net, test_data)
    print(f"Accuracy is {100*accuracy:.2f}%")     # Expected to be around 10%

    train_data = load_data("mnistdata/mnist_train.csv", delimiter=",", dtype=int)
    train(net, train_data)

    accuracy = test(net, test_data)
    print(f"Accuracy is {100*accuracy:.2f}%")
