#! /usr/bin/env python

import bisect
import sqlite3

import numpy as np


def readFromDatabase(dbfilepath, tableName, attributeList, dom):
    """
    Compute a multi-dimensional histogram from a table stored in an sqlite database
    'attributeList' contains names of attributes along with the domain min and domain max for the attribute.
    Tuples exceeding domain min and max are excluded
    Interval counts are for closed-open intervals [a,b) except for last interval in domain which is closed-closed
    """
    assert len(attributeList) == len(dom.dimensions), "Number of dimensions in dom does not match attributes"

    columnNames = [i[0] for i in attributeList]
    mins = [i[1] for i in attributeList]
    maxs = [i[2] for i in attributeList]
    dim = len(dom.dimensions)

    conn = sqlite3.connect(dbfilepath)
    c = conn.cursor()
    constants = columnNames + [tableName] + columnNames
    queryString = 'SELECT '
    queryString += ','.join(columnNames) + ', count(*) as cnt '
    queryString += 'FROM ' + tableName + ' '
    queryString += 'WHERE 1 ' + ''.join(
        [' AND %s BETWEEN %f AND %f ' % (columnNames[i], mins[i], maxs[i]) for i in range(dim)]) + ' '
    queryString += 'GROUP BY ' + ','.join(columnNames)
    c.execute(queryString)

    # translate bin lists to given domains
    # binBoundaries in Domain are ndarrays, so broadcasting works
    bins = []
    for i in range(dim):
        bins.append(dom.binBoundaries[i] * (maxs[i] - mins[i]) + mins[i])

    output = np.zeros(dom.dimensions, dtype=int)
    for row in c:
        cell = []
        for i in range(dim):
            cell.append(min(bisect.bisect_right(bins[i], row[i]) - 1, len(bins[i]) - 2))
        output[tuple(cell)] += row[dim]

    return output.flatten()


if __name__ == "__main__":
    main()
