from flatComputeViewDlsq import compute_dlsq_no_filter
import psycopg2
import numpy as np
from queryTruncationFreeJoin import main_query_LP_truncation_free_join
from ExtractInfo import mainExtractInfo
import pickle
import random


def main_svt_compute_threshold(list_filename, primary_path, key_path, query_path, out_info_path, views_path,
                               view_to_linkQuery_path, view_to_noLinkQuery_path, eps, global_sentivity):
    view_attr_set_list, view_primary_sub_all_list, view_primary_no_sub_all_list = compute_dlsq_no_filter(list_filename,
                                                                                                         primary_path,
                                                                                                         key_path,
                                                                                                         query_path,
                                                                                                         out_info_path)
    dlsq0_amount = get_dlsq0_amount(view_attr_set_list)
    eps_view = eps / (len(view_attr_set_list) - dlsq0_amount)
    eps_view_Qhat = eps_view * (1 / 4)
    eps_view_svt = eps_view - eps_view_Qhat
    for index, view in enumerate(view_attr_set_list):
        if (view[4] == 0):
            view_attr_set_list[index].append(None)
            print(view[4], None, view[3])
        else:
            svt_query_i = []  #
            view_dlsq = view[4]
            Q_hat_ldsql = Q_hat_ldsql = (float(compute_real_query(view[3])) + np.random.laplace(loc=0,
                                                                                                scale=view_dlsq / eps_view_Qhat)) * 1
            with open(query_path, 'w') as file:
                file.write(view[3])
            mainExtractInfo(
                ['-D', 'tpc-h-10', '-Q', query_path, '-P', primary_path, '-K', key_path, '-O', out_info_path])
            for i in range(1, global_sentivity):
                Q_tau = main_query_LP_truncation_free_join(['-I', out_info_path, '-T', i])
                # print(Q_tau,Q_hat_ldsql)
                svt_query_i.append((Q_tau - Q_hat_ldsql) / i)
            above_tau = above_threshold(svt_query_i, 0, eps_view_svt)
            view_attr_set_list[index].append(above_tau)
            print(view_dlsq, above_tau, view[3])
    str_view_primary_sub(view_primary_sub_all_list)
    str_view_no_primary_sub(view_primary_no_sub_all_list)
    pickle_write(view_attr_set_list, views_path)
    pickle_write(view_primary_sub_all_list, view_to_linkQuery_path)
    pickle_write(view_primary_no_sub_all_list, view_to_noLinkQuery_path)


def get_dlsq0_amount(view_attr_set_list):
    amount = 0
    for i in view_attr_set_list:
        if (i[4] == 0):
            amount += 1
    return amount


def str_view_primary_sub(view_primary_sub_all_list):
    for i, vi in enumerate(view_primary_sub_all_list):
        for j, vj in enumerate(vi):
            for k, vk in enumerate(vj):
                view_primary_sub_all_list[i][j][k] = str(vk)


def str_view_no_primary_sub(view_primary_no_sub_all_list):
    for i, vi in enumerate(view_primary_no_sub_all_list):
        for j, vj in enumerate(vi):
            view_primary_no_sub_all_list[i][j] = str(vj)


def pickle_write(data, path):
    with open(path, 'wb') as f:
        pickle.dump(data, f)


def above_threshold(queries, T, epsilon):
    T_hat = T + np.random.laplace(loc=0, scale=2 / epsilon)
    for idx, q in enumerate(queries):
        nu_i = np.random.laplace(loc=0, scale=4 / epsilon)
        if q + nu_i >= T_hat:
            return idx + 1
    # return random.randint(0,len(queries)-1)


def compute_real_query(query):
    conn = psycopg2.connect(database='tpc-h-10', user="postgres", password="root", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result[0][0]


if __name__ == "__main__":
    list_filename = ["../../dataQuery/tpch/query/original_query/base/count.sql",
                     "../../dataQuery/tpch/query/original_query/base/sum.sql"]
    primary_path = '../../basic/tpch/tpch_primary_relation.txt'
    key_path = '../../basic/tpch/tpch_key.txt'
    query_path = '../../information/tpch/noFilter/agg_no_filter_database_view_query.txt'
    out_info_path = '../../information/tpch/noFilter/out_info.txt'
    views_path = '../../views/tpch/views_information.pkl'
    view_to_linkQuery_path = '../../views/tpch/view_to_linkQuery.pkl'
    view_to_noLinkQuery_path = '../../views/tpch/view_to_noLinkQuery.pkl'
    main_svt_compute_threshold(list_filename, primary_path, key_path, query_path, out_info_path, views_path,
                               view_to_linkQuery_path, view_to_noLinkQuery_path, 10, 2 ** 16)  #
