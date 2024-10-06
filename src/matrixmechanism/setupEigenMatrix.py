#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import strategies as ss

import numpy as np

import matrixMechanism as mm


#
#  This is sample code demonstrating applications of the matrix mechanism
#

def matrix(W, A, x, epsilon):
    # Instantiate the matrix mechanism
    MMech = mm.MatrixMechanism(A, epsilon, delta=0)

    # Get noisy answers to the strategy matrix
    yy = MMech._noisyAnswer(x)
    # Do the inference to get x
    xx = MMech._inference(yy, nonNeg=False)
    y = np.dot(W, xx)
    return y


def main_eigen_matrix(x, W, epsilon):
    # print("A4: eigen:**********************************************************")

    trueAns = np.dot(W, x)

    MMech = mm.MatrixMechanism(ss.expDesign(W=W), epsilon, delta=0.01)
    # print('Expected total error for workload using eigen select method:', MMech.totalSquaredError(W))
    # print('Expected error for each query in the workload using eigen select method:\n', MMech.allSquaredErrors(W))

    np.random.seed(1)

    # Compute the noisy answers to strategy queries
    # Normally this is combined with inference by calling method MMech.privateEstimate(...)
    # but here we showcase the different inference methods
    yy = MMech._noisyAnswer(x)

    # Compute noisy estimate of the database counts
    xx = MMech._inference(yy, nonNeg=False)

    ans = np.dot(W, xx)

    xx2 = MMech._inference(yy, nonNeg=True)
    # print("noisy database",xx2)
    # print("real database",x)
    ans2 = np.dot(W, xx2)
    # The squared error of the workload query answers can be computed as follows:
    error = [x ** 2 for x in ans - trueAns]
    # # print('Squared errors, standard\n', error)
    # print('Total squared error:', sum(error), '\n')
    # print('Average squared error:', sum(error)/len(error), '\n')

    error2 = [x ** 2 for x in ans2 - trueAns]

    # # print('Squared errors, non-negative\n', error2)
    # print('Total squared error, non-negative:', sum(error2), '\n')
    # print('Average squared error, non-negative:', sum(error2)/len(error2), '\n')

    return xx, xx2, trueAns, ans, ans2, error, error2
