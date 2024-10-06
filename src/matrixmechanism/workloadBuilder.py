#! /usr/bin/env python

import itertools
import operator
import random
from functools import reduce

import numpy as np


def product(seq):
    """ Helper function to compute product of elements of a list. """
    return reduce(operator.mul, seq, 1)


def cummulativeDistributionWorkload(dimensions):
    """ Generate set of interval queries defining CDF
    For example, in one dimension of size n: (0,1), (0,2), (0,3) ... (0,n)
    """
    # create all pairs of variables in the multi-dimensional domain
    # these are tuples of arity 2*|dimensions|
    intervalList = []
    for d in dimensions:
        intervalList.append([(0, i) for i in range(d + 1)[1:]])
    crossproduct = list(itertools.product(*intervalList))
    return intervalsToMatrix(dimensions, crossproduct)


def onesetMarginal(seldims, dimensions):
    """ Generate all individual bucket queries on selected dimensions
    """
    curintervals = [list(zip([0] * len(dimensions), dimensions))]
    for curdim in seldims:
        newintervals = []
        for interval in curintervals:
            selinterval = interval
            for c1 in range(dimensions[curdim]):
                selinterval[curdim] = (c1, c1 + 1)
                newintervals.append(list(selinterval))

        curintervals = list(newintervals)

    return curintervals


def randomShapedRangeWorkload(dimensions, shape, number):
    """Generate random list of range queries of specified shape, represented as multi-dimensional intervals
    Example parameters: ( [4,4], [2,2], 5 )
    """

    totalIntervals = product(list(map(lambda i, j: i - j + 1, dimensions, shape)))
    assert totalIntervals >= number, 'number of queries is greater than all %s range queries of this form!' % str(
        totalIntervals)
    intervals = {}
    for i in range(len(dimensions)):
        lowerBoundaries = np.random.random_integers(0, dimensions[i] - shape[i],
                                                    number)  # generate left edges of query range randomly
        intervals[i] = [(X, X + shape[i]) for X in lowerBoundaries]  # create intervals
    result = []
    for j in range(number):
        tup = []
        for k in range(len(dimensions)):
            tup.append(intervals[k][j])
        result.append(tuple(tup))
    return intervalsToMatrix(dimensions, result)


def intervalsToMatrix(dimensions, mdIntervals):
    """Convert a list of multi-dimensional intervals into a matrix whose rows represent flattened multi-dimensional queries.
    mdIntervals is a list containing tuples of arity equal to the number of dimensions.
    Each element of a tuple is a pair representing an interval in one dimension
    """

    # define the right size matrix, of zeroes
    totalrows = len(mdIntervals)
    matrixDimensions = [totalrows]
    matrixDimensions.extend(dimensions)
    m = np.zeros(matrixDimensions)

    # set desired ranges of the matrix to 1
    row = 0
    for r in mdIntervals:  # r is tuple of 2-ary interval tuples
        indexes = [row]
        for interval in r:
            indexes.append(slice(interval[0], interval[1]))
        m[indexes] = 1
        row += 1

    # flatten multiple dimensions to get matrix.  Each row is a flattened high dim range query
    return m.reshape(totalrows, product(dimensions))


def intervalsToMinor(dimensions, mdIntervals):
    """Convert a list of multi-dimensional intervals into a matrix WtW where W is a matrix
    whose rows represent flattened multi-dimensional queries.
    mdIntervals is a list containing tuples of arity equal to the number of dimensions.
    Each element of a tuple is a pair representing an interval in one dimension
    """
    n = product(dimensions)
    m = len(mdIntervals)

    minor = np.zeros([n, n])
    for c in range(0, m, n):
        c1 = min(c + n, m)
        mat = np.array(intervalsToMatrix(dimensions, mdIntervals[c:c1]), 'd')
        minor = minor + np.dot(mat.T, mat)

    return minor


def rangeWorkloadGeneral(dimensions, sampleSize=None):
    """Generate a matrix of all high dimensional range queries, or sampled subset
    dimensions: a list of the size of each dimension
    e.g. rangeWorkloadGeneral( [8] )  returns all one-dimension range queries over domain of size 8
    e.g. rangeWorkloadGeneral( [2,4,4] )  returns all 3-dimension range queries over domains of size 2,4,4
    """

    # compute the cross-product of the intervals in each dimension
    # this represents all possible range queries
    intervalList = []
    for d in dimensions:
        intervalList.append(
            [(i, j + 1) for i in range(d) for j in range(i, d)])  # add list of all intervals on domain of size d
    crossproduct = list(itertools.product(*intervalList))

    # sample, if appropriate
    if sampleSize:
        assert sampleSize <= len(crossproduct), 'sampleSize is greater than all %s range queries!' % str(
            len(crossproduct))
        ranges = random.sample(crossproduct, sampleSize)
    else:
        ranges = crossproduct

    return intervalsToMatrix(dimensions, ranges)


def predicateWorkload(domain, sampleSize=None):
    '''Generate a matrix of random predicate queries, or all predicate queries if sampleSize is not specified
    The set of all predicate queries are all bitstrings of size 'domain'
    First generate a sample of integers. Then turn them into rows of a matrix (this avoids duplicates)
    '''
    if sampleSize:  # do sampling
        numbers = set()
        while len(numbers) < sampleSize:
            newnum = random.getrandbits(domain)
            numbers.add(newnum)
    else:  # generate all predicate queries
        numbers = range(2 ** domain)
    arr = []  # this will contain a list of each bit of each number in 'numbers'
    for i in numbers:  # enumeration below converts a decimal number to list of bits
        arr.extend([(i >> y) & 1 for y in range(domain - 1, -1, -1)])
    m = np.array(arr, dtype='d')
    return m.reshape(len(numbers), domain)


def allPredicateMinor(domain):
    """	Compute directly the minor product of workload W, that is: (W^t) * W, for the workload equal to all predicate queries.
    (This function is much faster than materializing W and computing the transpose and matrix product.)
    """
    minor = np.zeros([domain, domain], dtype=object)  # dtype=object uses python type of unlimited precision
    for i in range(domain):
        for j in range(domain):
            if i == j:
                minor[i][j] = 2 ** (domain - 1)
            else:
                minor[i][j] = 2 ** (domain - 2)
    return minor


def allRangeMinor(dimensions):
    """	Compute directly the minor product of workload W, that is: (W^t) * W
    for the workload equal to all range queries, defined for any multi-dimensional domain.
    (This function is much faster than materializing W and computing the transpose and matrix product.)
    """
    dim = len(dimensions)
    # create all pairs of variables in the multi-dimensional domain
    # these are tuples of arity 2*|dimensions|
    intervalList = []
    for d in dimensions:
        intervalList.append(list(range(d)))
    crossproduct = list(itertools.product(*intervalList, repeat=2))

    # set up minor, which must have an entry for each pair of domain variables
    minor = np.zeros(dimensions + dimensions, dtype=np.int32)

    # consider each pair of domain entries, computing covariance value
    for tup in crossproduct:
        var1 = tup[0:dim]
        var2 = tup[dim:2 * dim]
        # normalize variables to lower corner, upper corner
        nvar1, nvar2 = [0] * dim, [0] * dim
        for i in range(dim):
            nvar1[i] = min(var1[i], var2[i]) + 1 - 0
            nvar2[i] = dimensions[i] - max(var1[i], var2[i])
        minor[tup] = product(nvar1) * product(nvar2)
    return minor.reshape(product(dimensions), product(dimensions))


def allkwayMarginalMinor(dimensions, k):
    """	Compute directly the minor product of workload W, that is: (W^t) * W
    for the workload equal to all k-way marginal queries, defined for any multi-dimensional domain.
    (This function is much faster than materializing W and computing the transpose and matrix product.)
    """
    ndims = len(dimensions)
    minor = np.zeros(dimensions + dimensions)

    crossproduct = list(itertools.product(*list(map(range, dimensions)), repeat=2))
    for tup in crossproduct:
        var1 = tup[0:ndims]
        var2 = tup[ndims:]

        nstars = sum(map(operator.ne, var1, var2))
        if nstars > ndims - k:
            minor[tup] = 0
        elif nstars == ndims - k:
            minor[tup] = 1
        else:
            r = min(k, ndims - nstars - k)
            n = ndims - nstars
            minor[tup] = product(list(range(n - r + 1, n + 1))) / product(list(range(1, r + 1)))  # compute nCr

    return minor.reshape(product(dimensions), product(dimensions))


def allRangeMarginalMinor(dimensions, maxways):
    """	Compute directly the minor product of workload W, that is: (W^t) * W
    for the workload equal to all ranges over k-way marginal queries, defined for any multi-dimensional domain.
    (This function is much faster than materializing W and computing the transpose and matrix product.)
    """
    ndims = len(dimensions)
    minor = np.zeros(dimensions + dimensions)

    crossproduct = list(itertools.product(*list(map(range, dimensions)), repeat=2))
    for tup in crossproduct:
        var1 = tup[0:ndims]
        var2 = tup[ndims:]

        for c in range(maxways + 1):
            for seldims in itertools.combinations(list(range(ndims)), c):
                count = 1
                for dim in seldims:
                    count *= (min(var1[dim], var2[dim]) + 1) * (dimensions[dim] - max(var1[dim], var2[dim])) - 1

                minor[tup] += count

    return minor.reshape(product(dimensions), product(dimensions))


def main():
    dim = [4]
    print(cummulativeDistributionWorkload(dim))
    print(randomShapedRangeWorkload([4, 4], [2, 2], 5))
    print(rangeWorkloadGeneral([2, 2]))
    print(allkwayMarginalMinor([2, 2], 1))
    print(allRangeMarginalMinor([2, 2], 1))


if __name__ == "__main__":
    main()
