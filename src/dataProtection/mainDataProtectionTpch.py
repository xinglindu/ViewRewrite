import time
import sys
from svtComputeThresholdDLSQ import main_svt_compute_threshold as view_generate
# from svtComputeThresholdRealQuery import main_svt_compute_threshold as view_generate
from vectorization import main_vectorization as vectorization
from synopsisGenerate import main_synopsisGenerate as synopsis_generate


def view_generate_tpch(compute_tau_eps, global_sentivity, list_filename):
    list_filename = ["../../dataQuery/us/query/original_query/all/count.sql",
                     "../../dataQuery/us/query/original_query/all/sum.sql"]

    primary_path = '../../basic/tpch/tpch_primary_relation.txt'
    key_path = '../../basic/tpch/tpch_key.txt'
    query_path = '../../information/tpch/noFilter/agg_no_filter_database_view_query.txt'
    out_info_path = '../../information/tpch/noFilter/out_info.txt'
    views_path = '../../views/tpch/views_information.pkl'
    view_to_linkQuery_path = '../../views/tpch/view_to_linkQuery.pkl'
    view_to_noLinkQuery_path = '../../views/tpch/view_to_noLinkQuery.pkl'
    view_generate(list_filename, primary_path, key_path, query_path, out_info_path, views_path, view_to_linkQuery_path,
                  view_to_noLinkQuery_path, compute_tau_eps, global_sentivity)  #


def vectorization_tpch():
    views_path = '../../views/tpch/views_information.pkl'
    view_to_linkQuery_path = '../../views/tpch/view_to_linkQuery.pkl'
    view_to_noLinkQuery_path = '../../views/tpch/view_to_noLinkQuery.pkl'
    view_tau_path = '../../views/tpch/view_tau.pkl'
    view_vect_dict_path = '../../synopsis/tpch/real/syno_vect_dict.pkl'
    view_workload_vect_dict_path = '../../views/tpch/view_workload_vect_dict.pkl'
    view_df_path = '../../synopsis/tpch/real/view_df.pkl'
    key_path = '../../basic/tpch/tpch_key.txt'
    query_path = '../../information/tpch/noFilter/agg_no_filter_database_view_query.txt'
    out_info_path = '../../information/tpch/noFilter/out_info.txt'
    primary_path = '../../basic/tpch/tpch_primary_relation.txt'
    vectorization(views_path, view_to_linkQuery_path, view_to_noLinkQuery_path, view_tau_path, view_vect_dict_path,
                  view_workload_vect_dict_path, view_df_path, primary_path, key_path, query_path, out_info_path)


def synopsis_generate_tpch(synopsis_eps):
    view_tau_path = '../../views/tpch/view_tau.pkl'
    syno_vect_dict_path = '../../synopsis/tpch/real/syno_vect_dict.pkl'
    view_workload_vect_dict_path = '../../views/tpch/view_workload_vect_dict.pkl'
    syno_workload_path = '../../synopsis/tpch/protection/workload/syno_workload.pkl'
    syno_workload_non_negative_path = '../../synopsis/tpch/protection/workload/syno_workload_non_negative.pkl'
    syno_eigen_path = '../../synopsis/tpch/protection/eigen/syno_eigen.pkl'
    syno_eigen_non_negative_path = '../../synopsis/tpch/protection/eigen/syno_eigen_non_negative.pkl'
    # ans_eigen_path = '../../experiment/tpch/ans_eigen_dict.pkl'
    # error_eigen_path = '../../experiment/tpch/error_eigen_dict.pkl'
    synopsis_generate(view_tau_path, syno_vect_dict_path, view_workload_vect_dict_path, syno_workload_path,
                      syno_workload_non_negative_path, syno_eigen_path, syno_eigen_non_negative_path, synopsis_eps)


if __name__ == "__main__":
    database = 'tpc-h-10'
    if len(sys.argv) > 1:
        total_eps = float(sys.argv[1])
        # list_filename = [sys.argv[2]] #controlTpchWorkload1.sh
        list_filename = sys.argv[2].split(",")  # controlTpchWorkload2.sh
    else:
        total_eps = 8
        list_filename = []
    print('eps:', total_eps)
    print('workload', list_filename)
    compute_tau_eps = total_eps * (1 / 4)
    synopsis_eps = total_eps - compute_tau_eps
    global_sentivity = 2 ** 16
    view_generate_tpch(compute_tau_eps, global_sentivity, list_filename)
    vectorization_tpch()
    synopsis_generate_tpch(synopsis_eps)
