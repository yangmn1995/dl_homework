# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from reg_utils import sigmoid, relu, plot_decision_boundary, \
    initialize_parameters, load_2D_dataset, predict_dec
from reg_utils import compute_cost, predict, forward_propagation,\
    backward_propagation, update_parameters
import sklearn
import sklearn.datasets
import scipy.io
from testCases import *



def model(X, Y, learning_rate=0.3, num_iterations=30000, print_cost=True, lambd=0.,
          keep_prob=1):
    """

    :param X:
    :param Y:
    :param learning_rate:
    :param num_iterations:
    :param print_cost:
    :param lambd:
    :param keep_prob:
    :return:
    """
    grads = {}
    costs = []
    m = X.shape[1]
    layers_dims = [X.shape[0], 20, 3, 1]

    parameters = initialize_parameters(layers_dims)

    for i in range(num_iterations):

        if keep_prob == 1:
            a3, cache = forward_propagation(X, parameters)
        elif keep_prob < 1:
            a3, cache = forward_propagation_with_dropout(X, parameters, keep_prob)

        if lambd == 0:
            cost = compute_cost(a3, Y)
        else:
            cost = compute_cost_with_regularization(a3, Y, parameters, lambd)

        assert lambd == 0 or keep_prob == 1

        if lambd == 0 and keep_prob == 1:
            grads = backward_propagation(X, Y, cache)
        elif lambd != 0:
            grads = backward_propagation_with_regularization(X, Y, cache, lambd)
        elif keep_prob < 1:
            grads = backward_propagation_with_dropout(X, Y, cache, keep_prob)

        parameters = update_parameters(parameters, grads, learning_rate)

        if print_cost and i % 10000 == 0:
            print("cost after iteration {}: {}".format(i, cost))
        if print_cost and i % 10000 == 0:
            costs.append(cost)

    plt.plot(costs)
    plt.ylabel("cost")
    plt.xlabel("iterations (x1,000)")
    plt.title("Learning rate = " + str(learning_rate))
    plt.show()

    return parameters

def forward_propagation_with_dropout(X, parameters, keep_prob=0.5):
    np.random.seed(1)

    W1 = parameters["W1"]
    b1 = parameters["b1"]
    W2 = parameters["W2"]
    b2 = parameters["b2"]
    W3 = parameters["W3"]
    b3 = parameters["b3"]

    # l1 正常输出 A1
    Z1 = np.dot(W1, X) + b1
    A1 = relu(Z1)
    # l1 dropout
    D1 = np.random.rand(A1.shape[0], A1.shape[1])
    D1 = D1 < keep_prob
    A1 = A1 * D1
    A1 /= keep_prob

    # l2 正常输出 A2
    Z2 = np.dot(W2, A1) + b2
    A2 = relu(Z2)
    # l2 dropout
    D2 = np.random.rand(A2.shape[0], A2.shape[1])
    D2 = D2 < keep_prob
    A2 = D2 * A2
    A2 /= keep_prob

    Z3 = np.dot(W3, A2) + b3
    A3 = sigmoid(Z3)

    cache = (Z1, D1, A1, W1, b1, Z2, D2, A2, W2, b2, Z3, A3, W3, b3)

    return A3, cache



def compute_cost_with_regularization(A3, Y, parameters, lambd):
    """

    :param a3:
    :param Y:
    :return:
    """
    m = Y.shape[1]
    W1 = parameters["W1"]
    W2 = parameters["W2"]
    W3 = parameters["W3"]

    cross_entropy_cost = compute_cost(A3, Y)

    L2_regularization_cost = (lambd / 2. / m) * (np.sum(np.square(W1)) +
                                                 np.sum(np.square(W2)) +
                                                 np.sum(np.square(W3)))

    cost = cross_entropy_cost + L2_regularization_cost

    return cost

def backward_propagation_with_regularization(X, Y, cache, lambd):
    (Z1, A1, W1, b1, Z2, A2, W2, b2, Z3, A3, W3, b3) = cache
    m = Y.shape[1]

    dZ3 = A3 - Y

    dW3 = 1. / m * np.dot(dZ3, A2.T) + lambd / m * W3
    db3 = 1. / m * np.sum(dZ3, axis=1, keepdims=True)

    dA2 = np.dot(W3.T, dZ3)
    dZ2 = np.multiply(dA2, np.int64(A2 > 0))

    dW2 = 1. / m * np.dot(dZ2, A1.T) + lambd / m * W2
    db2 = 1. / m * np.sum(dZ2, axis=1, keepdims=True)

    dA1 = np.dot(W2.T, dZ2)
    dZ1 = np.multiply(dA1, np.int64(A1 > 0))

    dW1 = 1. / m * np.dot(dZ1, X.T) + lambd / m * W1
    db1 = 1. / m * np.sum(dZ1, axis=1, keepdims=True)



    gradients = {"dZ3": dZ3, "dW3": dW3, "db3": db3,
                 "dA2": dA2, "dZ2": dZ2, "dW2": dW2, "db2": db2,
                 "dA1": dA1, "dZ1": dZ1, "dW1": dW1, "db1": db1}

    return gradients


def backward_propagation_with_dropout(X, Y, cache, keep_prob):
    """

    :param X:
    :param Y:
    :param cache:
    :param keep_prob:
    :return:
    """
    m = X.shape[1]
    (Z1, D1, A1, W1, b1, Z2, D2, A2, W2, b2, Z3, A3, W3, b3) = cache

    # layer 3 backward
    dZ3 = A3 - Y
    dW3 = 1. / m * np.dot(dZ3, A2.T)
    db3 = 1. / m * np.sum(dZ3, axis=1, keepdims=True)
    dA2 = np.dot(W3.T, dZ3)
    # dropout 由于 dropout时 A中的值被dropout掉，所以相应的dA中的值也应该被dropout掉
    dA2 = dA2 * D2
    dA2 /= keep_prob

    # layer 2 backward
    dZ2 = np.multiply(dA2, np.int64(A2 > 0))
    dW2 = 1. / m * np.dot(dZ2, A1.T)
    db2 = 1. / m * np.sum(dZ2, axis=1, keepdims=True)
    # dropout
    dA1 = np.dot(W2.T, dZ2)
    dA1 = dA1 * D1
    dA1 /= keep_prob

    # layer 1 backward
    dZ1 = np.multiply(dA1, np.int64(A1 > 0))
    dW1 = 1. / m * np.dot(dZ1, X.T)
    db1 = 1. / m * np.sum(dZ1, axis= 1, keepdims= True)

    gradients = {"dZ3": dZ3, "dW3": dW3, "db3": db3,"dA2": dA2,
                 "dZ2": dZ2, "dW2": dW2, "db2": db2, "dA1": dA1,
                 "dZ1": dZ1, "dW1": dW1, "db1": db1}

    return gradients










if __name__ == '__main__':
    plt.rcParams['figure.figsize'] = (7.0, 4.0)  # set default size of plots
    plt.rcParams['image.interpolation'] = 'nearest'
    plt.rcParams['image.cmap'] = 'gray'

    train_X, train_Y, test_X, test_Y = load_2D_dataset()

    # parameters = model(train_X, train_Y)
    # print("On the training set:")
    # predictions_train = predict(train_X, train_Y, parameters)
    # print("On the test set:")
    # predictions_test = predict(test_X, test_Y, parameters)

    # A3, Y_assess, parameters = compute_cost_with_regularization_test_case()
    #
    # print("cost = " + str(compute_cost_with_regularization(A3, Y_assess, parameters, lambd=0.1)))

    # X_assess, Y_assess, cache = backward_propagation_with_regularization_test_case()
    #
    # grads = backward_propagation_with_regularization(X_assess, Y_assess, cache, lambd=0.7)
    # print("dW1 = " + str(grads["dW1"]))
    # print("dW2 = " + str(grads["dW2"]))
    # print("dW3 = " + str(grads["dW3"]))
    # parameters = model(train_X, train_Y, lambd = 0.6)
    # print ("On the train set:")
    # predictions_train = predict(train_X, train_Y, parameters)
    # print ("On the test set:")
    # predictions_test = predict(test_X, test_Y, parameters)

    # X_assess, parameters = forward_propagation_with_dropout_test_case()
    #
    # A3, cache = forward_propagation_with_dropout(X_assess, parameters, keep_prob=0.7)
    # print("A3 = " + str(A3))

    # X_assess, Y_assess, cache = backward_propagation_with_dropout_test_case()
    #
    # gradients = backward_propagation_with_dropout(X_assess, Y_assess, cache, keep_prob=0.8)
    #
    # print("dA1 = " + str(gradients["dA1"]))
    # print("dA2 = " + str(gradients["dA2"]))

    parameters = model(train_X, train_Y, keep_prob=0.86, learning_rate=0.3)

    print("On the train set:")
    predictions_train = predict(train_X, train_Y, parameters)
    print("On the test set:")
    predictions_test = predict(test_X, test_Y, parameters)

