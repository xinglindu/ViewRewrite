# fileQueryAnalysis
import sys
from fileQueryAnalysis import files_analysis
from fileQueryResponse import file_query_response
from accessControl.writeAnsPdDict import write_ans_eigen


def files_analysis_tpch(list_filename):
    list_filename = ["../../dataQuery/tpch/query/original_query/all/count.sql",
                     "../../dataQuery/tpch/query/original_query/all/sum.sql"]
    pass_queries_path = '../../dataQuery/tpch/query/pass_analysis_queries.sql'
    files_analysis(list_filename, pass_queries_path)


def file_query_response_tpch():
    pass_queries_path = ['../../dataQuery/tpch/query/pass_analysis_queries.sql']
    view_df_path = '../../synopsis/tpch/real/view_df.pkl'
    syno_workload_path = '../../synopsis/tpch/protection/workload/syno_workload.pkl'
    syno_eigen_path = '../../synopsis/tpch/protection/eigen/syno_eigen.pkl'
    syno_eigen_non_negative_path = '../../synopsis/tpch/protection/eigen/syno_eigen_non_negative.pkl'
    views_information_path = '../../views/tpch/views_information.pkl'
    ans_pd_dict = file_query_response(pass_queries_path, view_df_path, syno_eigen_path, views_information_path)
    ans_pd_dict = file_query_response(pass_queries_path, view_df_path, syno_eigen_path, views_information_path)


def write_ans_eigen_tpch():
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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # list_filename = [sys.argv[1]] #controlTpchWorkload1.sh
        list_filename = sys.argv[1].split(",")  # controlTpchWorkload2.sh
    else:
        list_filename = []
    files_analysis_tpch(list_filename)
    # file_query_response_tpch()
    write_ans_eigen_tpch()
