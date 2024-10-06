from svtComputeThresholdDLSQ import main_svt_compute_threshold as view_generate
from vectorization import main_vectorization as vectorization
from synopsisGenerate import main_synopsisGenerate as synopsis_generate


def view_generate_us(compute_tau_eps, global_sentivity):
    list_filename = ["../../dataQuery/us/query/original_query/all/count.sql",
                     "../../dataQuery/us/query/original_query/all/sum.sql"]
    primary_path = '../../basic/primary_relation.txt'
    key_path = '../../basic/primary_key.txt'
    query_path = '../../information/us/noFilter/agg_no_filter_database_view_query.txt'
    out_info_path = '../../information/us/noFilter/out_info.txt'
    views_path = '../../views/us/views_information.pkl'
    view_to_linkQuery_path = '../../views/us/view_to_linkQuery.pkl'
    view_to_noLinkQuery_path = '../../views/us/view_to_noLinkQuery.pkl'
    view_generate(list_filename, primary_path, key_path, query_path, out_info_path, views_path, view_to_linkQuery_path,
                  view_to_noLinkQuery_path, compute_tau_eps, global_sentivity)  #


def vectorization_us():
    views_path = '../../views/us/views_information.pkl'
    view_to_linkQuery_path = '../../views/us/view_to_linkQuery.pkl'
    view_to_noLinkQuery_path = '../../views/us/view_to_noLinkQuery.pkl'
    view_tau_path = '../../views/us/view_tau.pkl'
    view_vect_dict_path = '../../synopsis/us/real/syno_vect_dict.pkl'
    view_workload_vect_dict_path = '../../views/us/view_workload_vect_dict.pkl'
    view_df_path = '../../synopsis/us/real/view_df.pkl'
    key_path = '../../basic/primary_key.txt'
    query_path = '../../information/us/noFilter/agg_no_filter_database_view_query.txt'
    out_info_path = '../../information/us/noFilter/out_info.txt'
    primary_path = '../../basic/primary_relation.txt'
    vectorization(views_path, view_to_linkQuery_path, view_to_noLinkQuery_path, view_tau_path, view_vect_dict_path,
                  view_workload_vect_dict_path, view_df_path, primary_path, key_path, query_path, out_info_path)


def synopsis_generate_us(synopsis_eps):
    view_tau_path = '../../views/us/view_tau.pkl'
    syno_vect_dict_path = '../../synopsis/us/real/syno_vect_dict.pkl'
    view_workload_vect_dict_path = '../../views/us/view_workload_vect_dict.pkl'
    syno_workload_path = '../../synopsis/us/protection/workload/syno_workload.pkl'
    syno_workload_non_negative_path = '../../synopsis/us/protection/workload/syno_workload_non_negative.pkl'
    syno_eigen_path = '../../synopsis/us/protection/eigen/syno_eigen.pkl'
    syno_eigen_non_negative_path = '../../synopsis/us/protection/eigen/syno_eigen_non_negative.pkl'
    # ans_eigen_path = '../../experiment/us/ans_eigen_dict.pkl'
    # error_eigen_path = '../../experiment/us/error_eigen_dict.pkl'
    synopsis_generate(view_tau_path, syno_vect_dict_path, view_workload_vect_dict_path, syno_workload_path,
                      syno_workload_non_negative_path, syno_eigen_path, syno_eigen_non_negative_path, synopsis_eps)


if __name__ == "__main__":
    total_eps = 4
    compute_tau_eps = total_eps / 8
    synopsis_eps = total_eps - compute_tau_eps
    global_sentivity = 2 ** 16
    view_generate_us(compute_tau_eps, global_sentivity)
    vectorization_us()
    synopsis_generate_us(synopsis_eps)
