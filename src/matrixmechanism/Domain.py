#! /usr/bin/env python

import operator
from functools import reduce

import numpy as np


class Domain:
    """Description of domain for multidimensional histogram """

    def __init__(self, dimensions, binBoundaries=None):
        """ Construct domain object for given dimensions
            If binBoundaries omitted, then equi-width buckets are used in each dimensions.
            If binBoundaries is supplied, it should be a list of length equal to len(dimensions)
            Each element i of binBoundaries should be a sorted list of length equal to (dimension[i]+1)
            with first entry 0 and last entry 1
        """
        self.dimensions = dimensions
        if binBoundaries:
            self.binBoundaries = binBoundaries
        else:  # default to equi-width buckets in each dimenions
            self.binBoundaries = []
            for i in range(len(dimensions)):
                self.binBoundaries.append(np.linspace(0.0, 1.0, self.dimensions[i] + 1))

    def __str__(self):
        return 'DomainObject: ' + str(self.dimensions) + '\n' + str(self.binBoundaries)

    def size(self):
        return reduce(operator.mul, self.dimensions)


def main():
    # Creation of a multi-dimensional domain object (uniform buckets by default)
    dim = (2, 2, 4)
    d1 = Domain(dim)
    print(d1)

    # Creation of a multi-dimensional domain object (custom bucket boundaries)
    d2 = Domain(dim, [[0, .1, 1], [0, .3, 1], [0, .1, .2, .8, 1]])
    print(d2)


if __name__ == '__main__':
    main()
