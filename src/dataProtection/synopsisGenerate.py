import pickle
import numpy as np
import sys

sys.path.append('../matrixmechanism/')
from setupWorkloadMatrix import main_workload_matrix
from setupEigenMatrix import main_eigen_matrix
from collections import OrderedDict


def main_synopsisGenerate(view_tau_path, syno_vect_dict_path, view_workload_vect_dict_path, syno_workload_path,
                          syno_workload_non_negative_path, syno_eigen_path, syno_eigen_non_negative_path, eps_synopsis):
    syno_vect_dict = read_pickle(syno_vect_dict_path)
    view_workload_vect_dict = read_pickle(view_workload_vect_dict_path)
    view_tau_dict = read_pickle(view_tau_path)
    eps_signal_syno = eps_synopsis / len(syno_vect_dict)
    syno_workload_dict = OrderedDict()
    syno_workload_non_negative_dict = OrderedDict()
    syno_eigen_dict = OrderedDict()
    syno_eigen_non_negative_dict = OrderedDict()
    # ans_eigen_dict = OrderedDict()
    # error_eigen_dict = OrderedDict()
    for key in syno_vect_dict.keys():
        # print(key)
        tau = view_tau_dict[key]
        x = np.array(syno_vect_dict[key])
        W = np.vstack(view_workload_vect_dict[key])

        syno_eigen_dict[key] = None
        syno_eigen_non_negative_dict[key] = None
        syno_workload_dict[key] = None
        syno_workload_non_negative_dict[key] = None
        # ans_eigen_dict[key] = None
        # error_eigen_dict[key] = None
        try:
            if tau is None:
                syno_workload = x
                syno_workload_non_negative = x
                syno_eigen = x
                syno_eigen_non_negative = x
                syno_workload_dict[key] = syno_workload
                syno_workload_non_negative_dict[key] = syno_workload_non_negative
                syno_eigen_dict[key] = syno_eigen
                syno_eigen_non_negative_dict[key] = syno_eigen_non_negative
            else:
                syno_workload, syno_workload_non_negative = main_workload_matrix(x, W, eps_signal_syno / tau)
                syno_workload_dict[key] = syno_workload
                syno_workload_non_negative_dict[key] = syno_workload_non_negative
                syno_eigen, syno_eigen_non_negative, true_ans, privacy_ans, privacy_ans_non, error, error_non = main_eigen_matrix(
                    x, W, eps_signal_syno / tau)
                # ans_eigen_dict[key] = (true_ans,privacy_ans,privacy_ans_non)
                # error_eigen_dict[key] = (error,error_non)
                syno_eigen_dict[key] = syno_eigen
                syno_eigen_non_negative_dict[key] = syno_eigen_non_negative
        except MemoryError as e:
            print("Error!!!!!!!!!!!!!!!!!!!!!!!!!", e)
    write_pickle(syno_workload_dict, syno_workload_path)
    write_pickle(syno_workload_non_negative_dict, syno_workload_non_negative_path)
    write_pickle(syno_eigen_dict, syno_eigen_path)
    write_pickle(syno_eigen_non_negative_dict, syno_eigen_non_negative_path)
    # write_pickle(ans_eigen_dict,ans_eigen_path)
    # write_pickle(error_eigen_dict,error_eigen_path)


def write_pickle(data, path):
    with open(path, 'wb') as file:
        pickle.dump(data, file)


def read_pickle(path):
    with open(path, 'rb') as file:
        data = pickle.load(file)
    return data


if __name__ == "__main__":
    view_tau_path = '../../views/tpch/view_tau.pkl'
    syno_vect_dict_path = '../../synopsis/tpch/real/syno_vect_dict.pkl'
    view_workload_vect_dict_path = '../../views/tpch/view_workload_vect_dict.pkl'
    syno_workload_path = '../../synopsis/tpch/protection/workload/syno_workload.pkl'
    syno_workload_non_negative_path = '../../synopsis/tpch/protection/workload/syno_workload_non_negative.pkl'
    syno_eigen_path = '../../synopsis/tpch/protection/eigen/syno_eigen.pkl'
    syno_eigen_non_negative_path = '../../synopsis/tpch/protection/eigen/syno_eigen_non_negative.pkl'
    # ans_eigen_path = '../../experiment/tpch/ans_eigen_dict.pkl'
    # error_eigen_path = '../../experiment/tpch/error_eigen_dict.pkl'
    main_synopsisGenerate(view_tau_path, syno_vect_dict_path, view_workload_vect_dict_path, syno_workload_path,
                          syno_workload_non_negative_path, syno_eigen_path, syno_eigen_non_negative_path, 10)
