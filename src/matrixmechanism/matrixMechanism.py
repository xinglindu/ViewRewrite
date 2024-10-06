#! /usr/bin/env python
import math

import numpy as np
import numpy.linalg as la
import scipy.optimize as opt
import scipy.linalg as scla
import strategies as ss
import workloadClasses as wc
import numpy


# TODO-soluted: xinglin
# The MatrixMechanism class instantiates the matrix mechanism.
# 
# Use 
# 	xx = MM.privateEstimate(x) 
# to compute private estimate for input database x.  Private answers to workload queries in W may then be computed as:
# 	np.dot(W,xx)
# 
# To compute error of workload under instantiated matrix mechanims, use either of these:
# 
# 	MM.totalSquaredError(W)
# 	MM.allSquaredErrors(W)
# 
# Note that for some strategies, such as the wavelet and hierarchical strategies, more efficient algorithms exist for
# computing privateEstimate(x).  See [1,4].  This implementation offers generality by supporting arbitrary strategy matrices.


def L1sensitivity(A):
    """Return the L1 sensitivity of strategy matrix A: maximum L1 norm of the columns."""
    return float(la.norm(A, 1))  # implemented in numpy as 1-norm of matrix


def L2sensitivity(A):
    """Return the L2 sensitivity of strategy matrix A: maximum L2 norm of the columns (not the standard 2-norm of matrix)."""
    columnNorms = []
    for i in range(A.shape[1]):
        columnNorms.append(la.norm(A[:, i]))  # this norm is the 2-norm of a vector (here a column of the matrix)
    return float(max(columnNorms))


class MatrixMechanism:
    """Class representing the matrix mechanism instantiated with 'strategy'.
    If delta==0, standard epsilon differential privacy is implemented.
    Otherwise, epsilon-delta differential privacy is implemented.
    In either case, inference can be performed using standard least squares or non-negative least squares.
    """

    def __init__(self, strategy, epsilon, delta=0.0):
        self.setStrategy(strategy)
        self.setPrivacyParameter(epsilon, delta)

    def __str__(self):
        out = '[MatrixMechanism: '
        out += 'epsilon=' + str(self._epsilon)
        out += ' delta=' + str(self._delta)
        if self._nonNeg:
            out += ' nonNeg'
        out += ']'
        return out

    def setStrategy(self, strategy):
        """Set the strategy used in the mechanism"""
        self._A = strategy
        self._pinvA = None

    def getStrategy(self):
        """Get the strategy used in the mechanism"""
        return self._A

    def setPrivacyParameter(self, epsilon, delta):
        """Set epsilon and delta"""
        self._epsilon = epsilon
        self._delta = delta

        if self._delta == 0:  # constants for epsilon Diff Privacy
            self._sensitivity = L1sensitivity(self._A)
            self._noiseScale = self._sensitivity / float(self._epsilon)
            self._errorScale = 2.0 * (self._noiseScale ** 2)
        else:  # constants for epsilon-delta Diff Privacy
            self._sensitivity = L2sensitivity(self._A)
            self._noiseScale = self._sensitivity / float(self._epsilon) * math.sqrt(
                2.0 * math.log(2.0 / self._delta))  # using McSherry's L2 error bound
            self._errorScale = self._noiseScale ** 2

    def getPrivacyParameter(self):
        """Get epsilon and delta"""
        return self._epsilon, self._delta

    def privateEstimate(self, x, nonNeg=False):
        """ Return a private estimate of the input x by adding noise to the answers to the strategy queries,
        then inferring estimates for x.
        By default, use standard least squares.  If nonNeg = True, use non-negative least squares
        """
        b = self._noisyAnswer(x)
        return self._inference(b.reshape([self._A.shape[0]]), nonNeg)

    def _noisyAnswer(self, x):
        """ Return a noisy answer of the input x by adding noise to the answers to the strategy queries,
        """
        if self._delta == 0:  # use Laplace noise
            noise = np.random.laplace(0.0, self._noiseScale, self._A.shape[0])  # vector of scaled laplace noise
        else:  # use Gaussian noise
            noise = np.random.normal(0.0, self._noiseScale, self._A.shape[0])  # vector of scaled guassian noise
        return np.dot(self._A, x) + noise  # noisy answers to strategy queries

    def _inference(self, noisyX, nonNeg):
        """ Perform inference (either standard least squares, or non-neg least squares) on noisy input vector"""
        if nonNeg == False:  # standard least squares
            if self._pinvA == None:
                try:
                    self._pinvA = la.inv(self._A)
                except la.LinAlgError:  #
                    try:
                        self._pinvA = la.pinv(self._A)  # save this, to avoid recomputing in case of multiple calls
                    except la.LinAlgError:
                        # TODO-soluted: xinglin
                        self._pinvA = scla.pinv(self._A)

            return np.dot(self._pinvA, noisyX)
        else:  # non-neg least squares
            return opt.nnls(self._A, noisyX)[0]

    #	These functions compute squared error for a given workload under the defined matrix mechanism (using standard least squares inference)
    #	Error of the matrix mechanism is independent of the input data, so there is no input vector required.

    def totalSquaredError(self, W):
        """Return the total mean squared error of workload under current matrix mechanism.
        W can be a Workload object, or an ndarray type representing queries as one or more rows.
        """
        if type(W) is np.ndarray:  # this allows this function to work on workload represented as simple ndarray, not just Workload object
            WTW = np.dot(W.T, W)
        else:  # should be a Workload object
            WTW = W.minor()
        try:
            ATAinv = la.inv(np.dot(self._A.T, self._A))
        except la.LinAlgError:
            ATAinv = la.pinv(np.dot(self._A.T, self._A))  # save this, to avoid recomputing in case of multiple calls
        ATAinvWTW = np.dot(ATAinv, WTW)
        prof = np.trace(ATAinvWTW)
        return prof * self._errorScale

    def allSquaredErrors(self, W):
        """Return vector of mean squared errors, one for each query in workload W.
        Used to compute max error, or look at distribution of error over workload.
        W can be a Workload object, or an ndarray type representing queries as rows (including a single query)
        """
        if type(W) is np.ndarray:  # this allows this function to work on workload represented as simple ndarray, not just Workload object
            pass
        else:  # should be a Workload object
            W = W.matrix()
        try:
            ATAinv = la.inv(np.dot(self._A.T, self._A))
        except la.LinAlgError:
            ATAinv = la.pinv(np.dot(self._A.T, self._A))  # save this, to avoid recomputing in case of multiple calls
        W_ATAinv_WT = np.dot(np.dot(W, ATAinv), W.T)
        profileTerm = np.diag(W_ATAinv_WT)
        return profileTerm * self._errorScale

    def svdBound(self, W):
        """Return the SVD Bound for workload W under the instantiated mechanism
        W should be a workload class instance (not a matrix)
        """
        assert self._delta != 0, "SVD Bound is valid only for L2 matrix mechanism."
        return self._errorScale * W.svdBound()


def main():
    n = 2 ** 6  # set domain size

    # create workload of all range queries on one-dimensional domain of size n
    W = wc.AllRangeWorkload([n])

    ########### Analyze a few mechanisms:

    # create hierarchical strategy (branching 4) and wavelet strategy
    Hier = ss.regularHierarchicalStrategy([n], 4)
    Wav = ss.waveletStrategy([n])

    # Instatiate matrix mechanism for each strategy: epsilon differential privacy
    MM_Hier = MatrixMechanism(Hier, 0.1, delta=0.0)
    MM_Wav = MatrixMechanism(Wav, 0.1, delta=0.0)

    print('Under epsilon diff. privacy, total error for all range queries is lower for the hierarchical strategy:')
    print(MM_Hier.totalSquaredError(W), MM_Wav.totalSquaredError(W))

    # Instatiate matrix mechanism for each strategy: epsilon-delta differential privacy
    MM_Hier = MatrixMechanism(Hier, 0.1, delta=0.001)
    MM_Wav = MatrixMechanism(Wav, 0.1, delta=0.001)

    print('Under epsilon delta diff. privacy, total error for all range queries is lower for the wavelet strategy:')
    print(MM_Hier.totalSquaredError(W), MM_Wav.totalSquaredError(W), '\n')

    ############ Generate private data:

    x = [0] * n  # this is simply a vector of zeros for testing purposes

    # run matrix mechanism to get private output
    xx = MM_Hier.privateEstimate(x, nonNeg=False)
    print('Private Output, standard least squares\n', xx)

    # run matrix mechanism to get private output
    xx = MM_Hier.privateEstimate(x, nonNeg=True)
    print('Private Output, non-negative least squares\n', xx)


if __name__ == "__main__":
    main()
