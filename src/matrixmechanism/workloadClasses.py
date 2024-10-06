#! /usr/bin/env python

import itertools
import math
import random
import string

import numpy as np

import workloadBuilder as wb


class Workload:
    """ Base class representing a workload
    All workloads are created using 'dimensions' list, even in the case of one dimension
    E.g. [128]  or  [8,8]
    matrix is a matrix contains queries in the workload, one of each row
    sampleSize can be integer (number of samples) or float (percentage of maxCount)
    """

    def __init__(self, dimensions, matrix=None, sampleSize=None):
        self.name = 'Workload:' + 'dim=' + string.join([str(i) for i in dimensions], 'x') + ',samp=' + str(sampleSize)
        self._matrix = matrix
        self._minor = None
        self._pcklpath = None
        self.dimensions = dimensions
        self.domainSize = wb.product(dimensions)
        if type(sampleSize) == type(.1):
            self.sampleSize = int(sampleSize * self.maxCount())
        else:  # sampleSize int or None
            self.sampleSize = sampleSize
        assert (self.sampleSize < self.maxCount()), "%s samples cannot be choosen from set of %s possible queries!" % (
            self.sampleSize, self.maxCount())

    def numRows(self):
        return self.matrix().shape[0]

    def matrix(self):
        if self._matrix == None:
            self._matrix = np.zeros([0, wb.product(self.dimensions)])
        return self._matrix

    def minor(self):
        if self._minor == None:
            _minor = np.dot(self.matrix().T, self.matrix())
        return _minor

    def svdBoundMatrix(self):
        singvalues = np.linalg.svd(self.matrix(), compute_uv=0)
        bound = sum(singvalues)
        bound = bound ** 2
        return float(bound) / self.domainSize

    def svdBoundMinor(self):
        sqsingvalues = np.linalg.eigvalsh(self.minor())
        singvalues = list(map(math.sqrt, [max(x, 0) for x in sqsingvalues]))
        bound = sum(singvalues)
        bound = bound ** 2
        return float(bound) / self.domainSize

    def svdBound(self):
        return self.svdBoundMatrix()

    def __str__(self):
        return self.name


class PredicateWorkload(Workload):
    """Represents a workload consisting of a subset of predicate queries (i.e. 01-queries)
    Can be created in multiple dimensions, but this is equivalent to single dimension case
    E.g. All predicate queries over dimensions = [d1, ... dk] is equivalent to all predication queries over [d1 * d2 * ... * dk]
    """

    def __init__(self, dimensions, sampleSize=None):
        Workload.__init__(self, dimensions, None, sampleSize)
        self.name = 'Predicate' + self.name

    def maxCount(self):
        return 2 ** self.domainSize

    def matrix(self):
        if self._matrix == None:
            self._matrix = wb.predicateWorkload(self.domainSize, self.sampleSize)
        return self._matrix


# Workload consisting of all predicate queries (i.e. 01-queries)
# these functions overloaded for efficiency -- e.g. matrix is not materialized
class AllPredicateWorkload(PredicateWorkload):
    def __init__(self, dimensions):
        PredicateWorkload.__init__(self, dimensions, None)
        self.name = 'All' + self.name

    def numRows(self):
        return 2 ** self.domainSize

    def matrix(self):
        if self._matrix == None:
            self._matrix = wb.predicateWorkload(self.domainSize)
        return self._matrix

    def minor(self):
        if self._minor == None:
            self._minor = wb.allPredicateMinor(self.domainSize)
        return self._minor

    def svdBound(self):
        return self.svdBoundMinor()


class RangeWorkload(Workload):
    """ Represents a workload consisting of a subset of range queries, possibly multi-dimensional.
    """

    def __init__(self, dimensions, sampleSize=None):
        Workload.__init__(self, dimensions, None, sampleSize)
        self.name = 'Range' + self.name

    def maxCount(self):
        return wb.product([(x ** 2 + x) / 2 for x in self.dimensions])

    def matrix(self):
        if self._matrix == None:
            self._matrix = wb.rangeWorkloadGeneral(self.dimensions, self.sampleSize)
        return self._matrix


class AllRangeWorkload(RangeWorkload):
    """ Workload consisting of all range queries, possibly multi-dimensional.
    Computation of minor is overloaded here for efficiency.  Matrix never materialized.
    """

    def __init__(self, dimensions):
        RangeWorkload.__init__(self, dimensions, None)
        self.name = 'All' + self.name

    # matrix() not needed -- parent class will work (but shouldn't need to be materialized)

    def numRows(self):
        return wb.product([(x ** 2 + x) / 2 for x in self.dimensions])

    def minor(self):
        if self._minor == None:
            #	self._minor = wb.allRangeMinor( self.dimensions )
            self._minor = wb.allRangeMarginalMinor(self.dimensions, len(self.dimensions))
        return self._minor

    def svdBound(self):
        return self.svdBoundMinor()


class MarginalWorkload(Workload):
    """ Represents a workload consisting of a subset of marginal queries, possibly multi-dimensional.
    """

    def __init__(self, dimensions, nways, sampleSize=None):
        self._nways = list(nways)
        Workload.__init__(self, dimensions, None, sampleSize)
        self.name = 'Marginal' + str(self._nways) + self.name

    def maxCount(self):
        count = 0
        for c in self._nways:
            for seldims in itertools.combinations(self.dimensions, c):
                count += wb.product(seldims)
        return count

    def matrix(self):
        if self._matrix == None:
            ndims = len(self.dimensions)
            nwayintervals = []
            for c in self._nways:
                for seldims in itertools.combinations(list(range(ndims)), c):
                    nwayintervals.extend(wb.onesetMarginal(seldims, self.dimensions))
            if self.sampleSize:
                nwayintervals = random.sample(nwayintervals, self.sampleSize)

            self._matrix = wb.intervalsToMatrix(self.dimensions, nwayintervals)

        return self._matrix

    def minor(self):
        if self._minor == None:
            if self.sampleSize == None:
                self._minor = wb.allkwayMarginalMinor(self.dimensions, self._nways[0])
                for nway in self._nways[1:]:
                    self._minor = self._minor + wb.allkwayMarginalMinor(self.dimensions, nway)
            else:
                self._minor = np.dot(self.matrix().T, self.matrix())

        return self._minor


class RangeMarginalWorkload(Workload):
    """ Represents a workload consisting of a subset of ranges of marginal queries, possibly multi-dimensional.
    """

    def __init__(self, dimensions, maxways, sampleSize=None):
        self._maxways = maxways
        Workload.__init__(self, dimensions, None, sampleSize)
        self.name = 'RangeMarginal' + self.name

    def maxCount(self):
        count = 0
        for seldims in itertools.combinations(self.dimensions, self._maxways + 1):
            count += wb.product([(x + 1) * x / 2 for x in seldims]) - 1

        count += 1
        return count

    def matrix(self):
        if self._matrix == None:
            ndims = len(self.dimensions)
            nwayrangeintervals = []
            for c in range(self._maxways + 1):
                for seldims in itertools.combinations(list(range(ndims)), c):
                    rangebydim = [[[0, x]] for x in self.dimensions]
                    for dim in seldims:
                        rangebydim[dim] = [[0, x + 1] for x in range(self.dimensions[dim] - 1)]
                        rangebydim[dim].extend([[x, y + 1] for x in range(1, self.dimensions[dim]) for y in
                                                range(x, self.dimensions[dim])])

                    nwayrangeintervals.extend(itertools.product(*rangebydim))

            if self.sampleSize:
                nwayintervals = random.sample(nwayintervals, self.sampleSize)

            self._matrix = wb.intervalsToMatrix(self.dimensions, nwayrangeintervals)
        return self._matrix

    def minor(self):
        if self._minor == None:
            if self.sampleSize == None:
                self._minor = wb.allRangeMarginalMinor(self.dimensions, self._maxways)
            else:
                self._minor = np.dot(self.matrix().T, self.matrix())

        return self._minor

    def svdBound(self):
        return self.svdBoundMatrix()


class AllkwayMarginalWorkload(MarginalWorkload):
    """ Workload consisting of all range queries, possibly multi-dimensional.
    Computation of minor is overloaded here for efficiency.  Matrix never materialized.
    """

    def __init__(self, dimensions, nways):
        MarginalWorkload.__init__(self, dimensions, [nways])
        self.name = 'All' + str(nways) + 'way' + self.name

    # matrix() not needed -- parent class will work (but shouldn't need to be materialized)

    def numRows(self):
        return wb.product([x + 1 for x in self.dimensions]) - 1

    def svdBound(self):
        return self.svdBoundMinor()


def main():
    n = 4
    workloads = [
        PredicateWorkload([n], 4),
        AllPredicateWorkload([n]),
        RangeWorkload([n, n], 3),
        RangeWorkload([n, n], .5),
        AllRangeWorkload([n]),
        MarginalWorkload([n, n], [0]),
        AllkwayMarginalWorkload([n, n], 1),
        RangeMarginalWorkload([n, n], 2),
    ]

    for W in workloads:
        print(W.name)
        print(W.matrix())
        print(W.minor())
    exit()


if __name__ == "__main__":
    main()
