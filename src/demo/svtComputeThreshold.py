import numpy as np
from src.demo.svtUtils import Infix

Lap = lambda scale: np.random.laplace(0, scale)
DIV = Infix(lambda x, y: np.divide(x, y))


# def main_svt_compute_threshold():
#     1

def next_q_TSens(tsenses, Q_hat):
    tsenses = tsenses

    def _func():
        nonlocal tsenses
        i = 1
        shift = Q_hat - np.sum(tsenses)
        while True:
            tsenses = tsenses[tsenses > i]
            res = - ((np.sum(tsenses) + shift) | DIV | i)
            yield res
            i += 1

    return _func


def learn_threshold_TSens(tsenses, tsens_limit, eps):
    q_sens = 1
    c = 1
    eps_Qhat = eps | DIV | 10
    eps_tsens = eps - eps_Qhat
    Q_hat = np.sum(tsenses) + Lap(tsens_limit | DIV | eps_Qhat)
    # Q_hat = np.sum(tsenses)
    next_q = next_q_TSens(tsenses, Q_hat)
    res = SVT(next_q(), next_T(), q_sens, eps_tsens, c)
    threshold = len(res)
    return threshold


def SVT(next_q, next_T, q_sens, eps, c=1):
    res = []
    eps_1 = eps | DIV | 2
    eps_2 = eps - eps_1
    rou = Lap(q_sens | DIV | eps_1)
    count = 0
    while count < c:
        q = next_q.__next__()
        T = next_T.__next__()
        v = Lap((2 * c * q_sens) | DIV | eps_2)
        if q + v >= T + rou:
            res.append(True)
            count += 1
        else:
            res.append(False)
    return res


def next_T():
    while True:
        yield 0


if __name__ == "__main__":
    1
