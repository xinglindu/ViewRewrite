from fileQueryResponse import file_query_response
import pickle
import time


# ans_pd_dict = {'view':view_original_all_list,'query':query_all_list,'real_ans':real_ans_all_list,'privacy_ans':privacy_ans_all_list}
def write_ans_eigen(pass_queries_path, view_df_path, syno_eigen_path, syno_eigen_non_negative_path, ans_eigen_path,
                    ans_eigen_non_negative_path, views_information_path):
    ans_pd_dict = file_query_response(pass_queries_path, view_df_path, syno_eigen_path, views_information_path)
    ans_non_negative_pd_dict = file_query_response(pass_queries_path, view_df_path, syno_eigen_non_negative_path,
                                                   views_information_path)
    write_pickle(ans_eigen_path, ans_pd_dict)
    write_pickle(ans_eigen_non_negative_path, ans_non_negative_pd_dict)


def write_pickle(path, data):
    with open(path, 'wb') as file:
        pickle.dump(data, file)


if __name__ == "__main__":
    pass_queries_path = ['../../dataQuery/tpch/query/pass_analysis_queries.sql']
    view_df_path = '../../synopsis/tpch/real/view_df.pkl'
    syno_workload_path = '../../synopsis/tpch/protection/workload/syno_workload.pkl'
    syno_eigen_path = '../../synopsis/tpch/protection/eigen/syno_eigen.pkl'
    syno_eigen_non_negative_path = '../../synopsis/tpch/protection/eigen/syno_eigen_non_negative.pkl'
    ans_eigen_path = '../../experiment/tpch/ans_eigen_pd.pkl'
    ans_eigen_non_negative_path = '../../experiment/tpch/ans_eigen_non_negative_pd.pkl'
    views_information_path = '../../views/tpch/views_information.pkl'
    write_ans_eigen(pass_queries_path, view_df_path, syno_eigen_path, syno_eigen_non_negative_path, ans_eigen_path,
                    ans_eigen_non_negative_path, views_information_path)
