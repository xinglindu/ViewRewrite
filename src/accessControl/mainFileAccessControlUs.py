# fileQueryAnalysis

from fileQueryAnalysis import files_analysis
from fileQueryResponse import file_query_response
from accessControl.writeAnsPdDict import write_ans_eigen


def files_analysis_us():
    list_filename = ["../../dataQuery/us/query/original_query/all/count.sql",
                     "../../dataQuery/us/query/original_query/all/sum.sql"]
    pass_queries_path = '../../dataQuery/us/query/pass_analysis_queries.sql'
    files_analysis(list_filename, pass_queries_path)


def file_query_response_us():
    pass_queries_path = ['../../dataQuery/us/query/pass_analysis_queries.sql']
    view_df_path = '../../synopsis/us/real/view_df.pkl'
    syno_workload_path = '../../synopsis/us/protection/workload/syno_workload.pkl'
    syno_eigen_path = '../../synopsis/us/protection/eigen/syno_eigen.pkl'
    syno_eigen_non_negative_path = '../../synopsis/us/protection/eigen/syno_eigen_non_negative.pkl'
    views_information_path = '../../views/us/views_information.pkl'
    ans_pd_dict = file_query_response(pass_queries_path, view_df_path, syno_eigen_path, views_information_path)
    ans_pd_dict = file_query_response(pass_queries_path, view_df_path, syno_eigen_path, views_information_path)


def write_ans_eigen_us():
    pass_queries_path = ['../../dataQuery/us/query/pass_analysis_queries.sql']
    view_df_path = '../../synopsis/us/real/view_df.pkl'
    syno_workload_path = '../../synopsis/us/protection/workload/syno_workload.pkl'
    syno_eigen_path = '../../synopsis/us/protection/eigen/syno_eigen.pkl'
    syno_eigen_non_negative_path = '../../synopsis/us/protection/eigen/syno_eigen_non_negative.pkl'
    ans_eigen_path = '../../experiment/us/ans_eigen_pd.pkl'
    ans_eigen_non_negative_path = '../../experiment/us/ans_eigen_non_negative_pd.pkl'
    views_information_path = '../../views/us/views_information.pkl'
    write_ans_eigen(pass_queries_path, view_df_path, syno_eigen_path, syno_eigen_non_negative_path, ans_eigen_path,
                    ans_eigen_non_negative_path, views_information_path)


if __name__ == "__main__":
    files_analysis_us()
    # file_query_response_us()
    write_ans_eigen_us()
