#! /usr/bin/env python

import math
import sys

import cvxopt as cv
import numpy as np
from cvxopt import solvers

solvers.options['DSDP_MaxIts'] = 10000
solvers.options['DSDP_GapTolerance'] = 1E-5
solvers.options['DSDP_Monitor'] = 0

'''
weighting queries over L2 using experimental design 
only works for square strategies right now (rectangular case not tested yet)
input: WtW (can be provided as Wtw or (Q^T)^-1 WtW Q^-1 ) and a set of queries(Q) to be selected from
the optimality can be known by the status output in the debug mode
'''


def expDesign(WtW, D0, Q, _debug=False):
    if WtW is not None:
        n = WtW.shape[0]
        D = np.diag(np.dot(np.dot(np.matrix(Q.T).I, WtW), np.matrix(Q).I))
        D = [max(0, x) for x in D]
    elif D0 is not None:
        n = Q.shape[0]
        D = [max(0, x) for x in D0]
    else:
        assert False, "Either WtW or D0 should be provided."

    D = np.array(D)
    locs = np.where(np.array(D) != 0)[0]
    Q1 = Q[locs, :]
    Qsq = np.multiply(Q1, Q1).T
    if D.sum() > 1E05 * Qsq.sum(axis=1).max():
        D = (D / (D.sum() / float(1E05)) / Qsq.sum(axis=1).max())

    m = len(locs)
    D1 = cv.matrix([0.0] * m + np.array(D)[locs].tolist())

    if _debug:
        solvers.options['DSDP_Monitor'] = 1

    # linear constraints
    Gl = cv.matrix(np.hstack([Qsq, np.zeros_like(Qsq)]))
    hl = cv.matrix([1.0] * Qsq.shape[0])

    # semi-definite constraints
    Gs = [cv.spmatrix(-1.0, list(range(0, 4 * m * m, 2 * m + 1)), list(range(2 * m)))]
    hs = [cv.matrix(np.vstack(
        [np.hstack([np.diag([0.0] * m), np.diag([1.0] * m)]), np.hstack([np.diag([1.0] * m), np.diag([0.0] * m)])]))]

    sol = solvers.sdp(D1, Gl, hl, Gs, hs, solver='dsdp')
    if _debug:
        print('status: ', sol['status'])
        sys.stdout.flush()

    res = list(map(math.sqrt, [max(x, 0) for x in sol['x'][:m]]))
    return np.dot(np.diag(res), Q1)
