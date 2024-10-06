#! /usr/bin/env python

import numpy as np

import DataReader as dr
import Domain as do
import matrixMechanism as mm
import strategies as ss


#
#  This is sample code demonstrating applications of the matrix mechanism
#

def main():
    print("""
	The sample database has schema: Sample(name, gradyear, gender, gpa) 
	It is stored in 'sample.sqlite', an sqlite database file containing the following records:
	
	"Alice" 	"2012"	"0"	"3.58"
	"Bob"		"2011"	"1"	"2.891"
	"Charlie"	"2013"	"0"	"3.325"
	"Dave"  	"2014"	"0"	"3.677"
	"Edgar" 	"2012"	"1"	"3.112"
	"Franklin"	"2013"	"0"	"3.987"
	"Griffin"	"2014"	"0"	"3.241"
	"Haley"		"2012"	"1"	"3.443"
	"Ignatius"	"2012"	"0"	"3.952"
	"Julius"	"2014"	"0"	"2.342"
	"Kim"		"2013"	"1"	"3.41"

	In this example, we consider 2-dimensional counts for the 'gradyear' and 'gender' attributes.
	The domain is defined to divide the 'gradyear' into 4 buckets and 'gender' into 2 buckets.	
	""")
    dom = do.Domain([4, 2])

    # Read from the database to represent it as a vector of counts.
    # For each attribute, the min and max value of the domain is specified.
    # (This is not, in general, the min and max values of a given datbase instance)
    attributeList = [
        ('gradyear', 2011, 2015),
        ('gender', 0, 1)]
    dbfilepath = './sample.sqlite'
    tableName = 'sample'
    x = dr.readFromDatabase(dbfilepath, tableName, attributeList, dom)

    print("""
	Once we read from the database, we work with the 2 dimensional representation of the database.
	Rows represent counts for gradyear in [2011,2012) [2012,2013) [2013,2014) [2014,2015]
	Columns represent counts for gender in [0,.5) [.5,1]
	""")
    print(x.reshape([4, 2]), '\n')

    print("""
	Actually, we always flatten the database counts so that they form a (1 x n) vector.
	The flattened vector contains [ row1, row2, ... ]
	The flattened vector representation of the database is:
	""")
    print(type(x))

    print("""
	Now we will write some linear counting queries. Queries are expressed as row vectors.  
	Query answers can be computed by the dot product of the query vector with x.
	""")

    Q = [None] * 5
    Q[0] = np.array([1, 1, 1, 1, 1, 1, 1, 1])
    print('Q0, the count of all students in the database:', Q[0])
    print('Q0, answer:', np.dot(Q[0], x), '\n')

    Q[1] = np.array([1, 1, 1, 1, 0, 0, 0, 0])
    print('Q1, the count of students with gradyear in [2011, 2012):', Q[1])
    print('Q1, answer:', np.dot(Q[1], x), '\n')

    Q[2] = np.array([0, 1, 0, 1, 0, 0, 0, 0])
    print('Q2, the count of female students with gradyear in [2011, 2012):', Q[2])
    print('Q2, answer:', np.dot(Q[2], x), '\n')

    Q[3] = np.array([1, 0, 1, 0, 0, 0, 0, 0])
    print('Q3, the count of male students with gradyear in [2011, 2012):', Q[3])
    print('Q3, answer:', np.dot(Q[3], x), '\n')

    Q[4] = np.array([0, 0, 0, 0, 1, 1, -1, -1])
    print('Q4, the difference between the number of 2013 grads and 2014 grads:', Q[4])
    print('Q4, answer:', np.dot(Q[4], x), '\n')

    print("""	A workload of queries is a matrix whose rows are queries.
	The workload matrix W combining the five queries above is:
	""")
    W = np.array(Q)
    print(W, '\n')

    print("""	The answer to all queries in the workload is computed by matrix multiplication, W ** x
	This returns a (column) vector of the true query answers:
	""")
    trueAns = np.dot(W, x)
    print(trueAns)

    print("""
	Next we answer these queries privately.
	The matrix mechanism must be instantiated with a strategy matrix. 
	Consider the following three alternatives:
	""")

    print("""	The first strategy is the workload itself.  This is closely related to using the
	standard Laplace mechanism to answer each query (although inference can still improve things in some cases.)
	""")
    A1 = W
    print(A1, '\n')

    print("""	The second strategy is the identity matrix.  This corresponds to computing the count
	in each bucket independently, then using them to compute the workload queries.
	""")
    A2 = np.diag([1] * 8)
    print(A2, '\n')

    print("""	Notice that the first and third column of the workload matrix are the same.  The counts of bucket 1 and 3
	are always used together in the workload queries.  This suggests it may be advantageous to compute their 
	sum separately, just once.  A similar rationale applies to the second and fourth column, the fifth and sixth 
	column, and the seventh and eighth column.  This leads to the following matrix as our third strategy, which
	has lower sensitivity than the workload.
	""")
    A3 = np.array([
        [1, 0, 1, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 1]
    ])
    print(A3, '\n')

    print("""
	Now we compare these three strategies by computing their expected error under standard inference.
	The epsilon is set to be 0.5 and delta is set to 0.01, so that epsilon-delta differential privacy is implemented.
	""")

    # Specify privacy parameters and instantiate the matrix mechanism

    epsilon = .5
    MMech = mm.MatrixMechanism(A1, epsilon, delta=0.01)
    print('Expected total error for workload using strategy A1:', MMech.totalSquaredError(W))
    print('Expected error for each query in the workload using strategy A1:\n', MMech.allSquaredErrors(W), '\n')

    MMech = mm.MatrixMechanism(A2, epsilon, delta=0.01)
    print('Expected total error for workload using strategy A2:', MMech.totalSquaredError(W))
    print('Expected error for each query in the workload using strategy A2:\n', MMech.allSquaredErrors(W), '\n')

    MMech = mm.MatrixMechanism(A3, epsilon, delta=0.01)
    print('Expected total error for workload using strategy A3:', MMech.totalSquaredError(W))
    print('Expected error for each query in the workload using strategy A3:\n', MMech.allSquaredErrors(W), '\n')

    MMech = mm.MatrixMechanism(ss.expDesign(W=W), epsilon, delta=0.01)
    print('Expected total error for workload using eigen select method:', MMech.totalSquaredError(W))
    print('Expected error for each query in the workload using eigen select method:\n', MMech.allSquaredErrors(W))

    print("""
	Since strategy A3 has lower expected error, we use it to compute answers to the workload queries.
	""")
    np.random.seed(1)

    # Compute the noisy answers to strategy queries
    # Normally this is combined with inference by calling method MMech.privateEstimate(...)
    # but here we showcase the different inference methods
    yy = MMech._noisyAnswer(x)

    # Compute noisy estimate of the database counts
    xx = MMech._inference(yy, nonNeg=False)
    print('The noisy database counts are:\n', xx, '\n')

    print("""	The noisy answers to the workload queries are computed by matrix multiplication, W ** (noisy x)
	This returns a (column) vector:
	""")
    ans = np.dot(W, xx)
    print(ans, '\n')

    print("""	Notice that the noisy database counts contain negative numbers.  An alternative inference
	process in the matrix mechanism applies non-negativity constraints.
	""")
    xx2 = MMech._inference(yy, nonNeg=True)
    print('Noisy database counts, non-negative: \n', xx2, '\n')

    print("""	The workload queries can be recomputed using these noisy counts instead.
	""")

    ans2 = np.dot(W, xx2)
    print('Alternative noisy workload query answers\n', ans2, '\n')

    # The squared error of the workload query answers can be computed as follows:
    error = [x ** 2 for x in ans - trueAns]
    print('Squared errors, standard\n', error)
    print('Total squared error:', sum(error), '\n')

    error2 = [x ** 2 for x in ans2 - trueAns]
    print('Squared errors, non-negative\n', error2)
    print('Total squared error:', sum(error2), '\n')


if __name__ == "__main__":
    main()
