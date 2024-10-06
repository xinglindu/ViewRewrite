#! /usr/bin/env python

import itertools
import math
import operator
from functools import reduce

import numpy as np

# external strategies
import expDesign as expD


# end of external stategies

def product(seq):
    """ Helper function to compute product of elements of a list. """
    return reduce(operator.mul, seq, 1)


def identityStrategy(n):
    return np.eye(n, dtype=int)


def waveMat(n):
    """Wavelet strategy matrix
    Based on "Differential Privacy via Wavelet Transforms", Xiao et al. ICDE 2010
    Generate one dimensional wavelet strategy matrix when n=2^k"""

    assert math.floor(math.log(n, 2)) - math.log(n, 2) == 0, 'n must be a power of 2'

    if n == 2:
        return np.matrix([[1, 1], [1, -1]], 'd')
    else:
        m = n / 2
        submat = waveMat(m)[1:]
        mat = np.vstack([np.hstack([submat, np.zeros([m - 1, m])]), np.hstack([np.zeros([m - 1, m]), submat])])
        mat = np.vstack([np.matrix([[1] * n, [1] * m + [-1] * m]), mat])
        return np.matrix(mat)


def fourierStrategy(n, WtW=None):
    """Fourier strategy matrix
    Based on "Privacy, Accuracy, and Consistency Too: A Holistic Solution to Contingency Table Release",
    Barak et al. PODS 2007
    Generate one dimensional fourier strategy matrix when n=2^k
    Can be adapted with specific workload W"""
    assert math.floor(math.log(n, 2)) - math.log(n, 2) == 0, 'n must be a power of 2'

    if n == 1:
        return np.matrix([1], 'd')
    else:
        _submatrix = fourierStrategy(n / 2)
        _matrix = np.hstack([np.vstack([_submatrix, _submatrix]), np.vstack([-_submatrix, _submatrix])]) / math.sqrt(2)

        if WtW is not None:
            assert n == WtW.shape[1], 'n must be equal to the number of columns of W'
            effRows = np.where(np.diag(np.dot(np.dot(_matrix, WtW), _matrix.T)) > 0)[0]
            return _matrix[effRows]
        else:
            return _matrix


def buildHierarchical(start, end, n, factors):
    """Builds a hierarchical strategy matrix with branching
    factor determined by the ordered list 'factoring'
    domain size will be the product of the factors
    (for efficiency, we build list of lists, to be converted to matrix later)"""

    m = [[0] * n]
    m[0][start:end + 1] = [1] * (end + 1 - start)
    if len(factors) >= 1:
        b = factors.pop(0)
        inc = (end - start + 1) / b
    else:
        return m
    for i in range(start, end + 1, inc):
        m = m + buildHierarchical(i, i + inc - 1, n, factors[:])
    return m


def factorStrategy(fact):
    """Return hierarchical strategy matrix given ordered list of branching factors 'fact'
    E.g. factorStrategy( [2,2,2] ) returns binary H on domain 8"""

    n = reduce(operator.mul, fact, 1)
    return np.array(buildHierarchical(0, n - 1, n, fact[:]), 'd')


def oneDimStrategyCombine(Aset):
    """Build a multi-dimensional strategy via multiple one dimensional strategies
    Each strategy matrix is applied to one dimension
    The strategies matrices are provided in Aset as a list of ndarrays"""
    matSizes, dimSizes = list(map(list, list(zip(*list(map(np.shape, Aset))))))
    domSize = reduce(operator.mul, dimSizes, 1)
    nquery = reduce(operator.mul, matSizes, 1)
    nDim = len(dimSizes)

    _matrix = np.zeros(matSizes + dimSizes)
    crossproduct = list(itertools.product(*(list(map(range, matSizes)) + list(map(range, dimSizes)))))

    for tup in crossproduct:
        var1 = tup[0:nDim]
        var2 = tup[nDim:]

        val = 1
        for c in range(nDim):
            val *= Aset[c][var1[c], var2[c]]

        _matrix[tup] = val

    return _matrix.reshape([nquery, domSize])


def waveletStrategy(dims):
    """Return strategy matrix by applying the wavelet strategy on each dimension
    The size of dimensions are given in order in 'dims'
    E.g. waveletStrategy( [2,8,4] ) returns the wavelet strategy on a 3 dimensional domain
    the size of the first dimension is 2, the second dimension is 8 and the third dimension is 4"""
    return oneDimStrategyCombine(list(map(waveMat, dims)))


def hierarchicalStrategy(factors):
    """Return strategy matrix by applying the hierarchical strategy on each dimension
    The factors used on each dimesion are in list 'factors'
    E.g. hierarchicalStrategy( [ [2,2,2], [4], [2,2] ] ) returns a strategy matrix on a 3 dimensional domain
    the size of the first dimension is 8, the second dimension is 4 and the third dimension is 4.
    The strategy applies a binary hierarachical on the first dimension, a quad hierarchical on the second
    dimension and a binary hierarchical on the third dimension"""
    return oneDimStrategyCombine(list(map(factorStrategy, factors)))


def regularHierarchicalStrategy(dimensions, order):
    """ Helper function to build hierarchical strategies which use the same branching factor 'order' in all dimensions """
    factorList = [[order] * int(math.log(d, order)) for d in dimensions]
    assert [product(l) for l in factorList] == dimensions, 'at least one dimension is not a product of "order"'
    return hierarchicalStrategy(factorList)


def expDesign(W=None, Ww=None, Qmat=None):
    """Experimental design method on L2
    The input is the workload matrix W (or be provided as WtW) and a set of queries Qmat to be selected from.
    Qmat is set fo be the eigen vectors of WtW by default.
    """
    if Qmat is None:
        """Use eigen basis as the default"""
        if W is not None:
            D, Q = np.linalg.svd(W, full_matrices=0)[1:]
        elif Ww is not None:
            D, Qt = np.linalg.eigh(Ww)
            Q = Qt.T
        else:
            assert False, "Either W or WtW must be provided."

        A = expD.expDesign(None, D, Q)
    else:
        Q = np.array(Qmat)
        if Ww is not None:
            A = expD.expDesign(Ww, None, Q)
        elif W is not None:
            A = expD.expDesign(np.dot(W.T, W), None, Q)
        else:
            assert False, "Either W or WtW must be provided."

    AtA = np.dot(A.T, A)

    """Fill the columns to have the same sensitivity"""
    m = max(np.diag(AtA))
    for c in range(len(AtA)):
        AtA[c, c] = m

    Da, Qa = np.linalg.eigh(AtA)
    return np.dot(np.diag([math.sqrt(max(x, 0)) for x in Da]), Qa.T)


def main():
    # Construct one-dimensional wavelet strategy matrix on domain of size 8
    W = waveletStrategy([4])
    print('Wavelet, n=4\n', W, '\n')

    # Construct fourier strategy matrix on domain of size 8
    W = fourierStrategy(8)
    print('Fourier, n=8\n', W, '\n')

    # Construction one-dimensional binary hierarchical strategy matrix on domain of size 8
    H = regularHierarchicalStrategy([8], 2)
    print('Binary hierarchical, n=8\n', H, '\n')

    # Construct two-dimensional wavelet strategy matrix on domains of size 4 and 4
    W = waveletStrategy([4, 4])
    print('2-dim Wavelet, n=4x4\n', W, '\n')

    # Construct two-dimensional hierarchical strategy matrix, with binary branching, on domains of size 4 and 4
    H = regularHierarchicalStrategy([4, 4], 2)
    print('Binary hierarchical, n=4x4\n', H, '\n')


if __name__ == "__main__":
    main()
