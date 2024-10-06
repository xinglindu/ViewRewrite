from fileViewGenerate import file_generate_view
import pickle
import sqlparse
import sys

sys.path.append('../dataProtection/')
from utilsConvert import get_token_list_type, get_query_where, get_token_list_name
from collections import OrderedDict
import numpy as np
import psycopg2


def file_query_response(pass_queries_path, view_df_path, syno_eigen_path, views_information_path):
    view_original_all_list = []
    query_all_list = []
    real_ans_all_list = []
    privacy_ans_all_list = []
    view_primary_sub_re, orig_query_primary_sub, view_primary_no_sub_re, orig_query_primary_no_sub = file_generate_view(
        pass_queries_path)
    # print(len(view_primary_sub_re))
    view_df = pickle_read(view_df_path)
    syno_eigen = pickle_read(syno_eigen_path)
    if len(view_primary_no_sub_re) > 0:
        view_original_list, query_list, real_ans_list, privacy_ans_list = view_primary_no_sub_response(view_df,
                                                                                                       syno_eigen,
                                                                                                       view_primary_no_sub_re,
                                                                                                       orig_query_primary_no_sub,
                                                                                                       views_information_path)
        view_original_all_list.extend(view_original_list)
        query_all_list.extend(query_list)
        real_ans_all_list.extend(real_ans_list)
        privacy_ans_all_list.extend(privacy_ans_list)
    if len(view_primary_sub_re) > 0:
        view_original_list, query_list, real_ans_list, privacy_ans_list = view_primary_sub_response(view_df, syno_eigen,
                                                                                                    view_primary_sub_re,
                                                                                                    orig_query_primary_sub,
                                                                                                    views_information_path)
        view_original_all_list.extend(view_original_list)
        query_all_list.extend(query_list)
        real_ans_all_list.extend(real_ans_list)
        privacy_ans_all_list.extend(privacy_ans_list)
    ans_pd_dict = {'view': view_original_all_list, 'query': query_all_list, 'real_ans': real_ans_all_list,
                   'privacy_ans': privacy_ans_all_list}
    # print(len(ans_pd_dict['view']))
    return ans_pd_dict


def get_view(path):
    view_dict = OrderedDict()
    view_information = read_pickle(path)
    for i in view_information:
        view_dict[(i[0], i[1])] = i[2]
    return view_dict


def read_pickle(path):
    with open(path, 'rb') as file:
        loaded_data = pickle.load(file)
    return loaded_data


def view_primary_sub_response(view_df, syno_eigen, view_primary_sub_re, orig_query_primary_sub, views_information_path):
    view_original_list = []
    query_list = []
    real_ans_list = []
    privacy_ans_list = []
    view_information = get_view(views_information_path)
    for i, value_list in enumerate(view_primary_sub_re):
        try:
            views_key = []
            for j, value in enumerate(value_list):
                key = value[0]
                query = value[1]
                if 'sub_query' in query:
                    query = query.replace("'sub_query'", str(int(sub_query_result)))
                # print(query)
                key_df_view = view_df[key]
                df_sign = key_df_view.copy()
                columns = df_sign.columns
                new_columns = {columns[-1]: 'sign'}
                df_sign = df_sign.rename(columns=new_columns)
                df_sign = df_sign.applymap(lambda x: True)
                try:
                    statement = sqlparse.parse(query)[0]
                    query_where = get_query_where(statement.tokens)
                    for sub in query_where.get_sublists():
                        sub_list = get_token_list_name(sub.tokens)
                        for itwo, two in enumerate(sub_list):
                            if (two == '='):
                                sub_list[itwo] = '=='
                        evall = 'x' + ''.join(sub_list[1:])
                        df_sign[sub_list[0]] = key_df_view[sub_list[0]].apply(lambda x: True if eval(evall) else False)
                except ValueError:
                    pass

                df_sign['sign'] = df_sign.iloc[:, :-1].all(axis=1)
                df_sign['sign'] = df_sign['sign'].replace({True: 1, False: 0})
                query_workload = list(df_sign.iloc[:, -1])
                sub_query_result = np.dot(query_workload, syno_eigen[key])
                views_key.append((key[0], view_information[key]))
            protection_ans = sub_query_result
            real_ans = compute_real_query(orig_query_primary_sub[i])
            # print(views_key,orig_query_primary_sub[i],protection_ans,real_ans)
            # print(orig_query_primary_sub[i],protection_ans,real_ans)
            view_original_list.append(tuple(views_key))
            query_list.append(orig_query_primary_sub[i])
            real_ans_list.append(real_ans)
            privacy_ans_list.append(protection_ans)
        except TypeError:
            print(orig_query_primary_sub[i], "!")
    return view_original_list, query_list, real_ans_list, privacy_ans_list


def view_primary_no_sub_response(view_df, syno_eigen, view_primary_no_sub_re, orig_query_primary_no_sub,
                                 views_information_path):
    # print(syno_eigen.keys())
    view_original_list = []
    query_list = []
    real_ans_list = []
    privacy_ans_list = []
    views_information = get_view(views_information_path)
    for i, value in enumerate(view_primary_no_sub_re):

        key = value[0]
        try:
            query = value[1]
            key_df_view = view_df[key]
            df_sign = key_df_view.copy()
            columns = df_sign.columns
            new_columns = {columns[-1]: 'sign'}
            df_sign = df_sign.rename(columns=new_columns)
            df_sign = df_sign.applymap(lambda x: True)
            try:
                statement = sqlparse.parse(query)[0]
                query_where = get_query_where(statement.tokens)
                for sub in query_where.get_sublists():
                    sub_list = get_token_list_name(sub.tokens)
                    for itwo, two in enumerate(sub_list):
                        if (two == '='):
                            sub_list[itwo] = '=='
                    evall = 'x' + ''.join(sub_list[1:])
                    df_sign[sub_list[0]] = key_df_view[sub_list[0]].apply(lambda x: True if eval(evall) else False)
            except ValueError:
                pass
            df_sign['sign'] = df_sign.iloc[:, :-1].all(axis=1)
            df_sign['sign'] = df_sign['sign'].replace({True: 1, False: 0})
            query_workload = list(df_sign.iloc[:, -1])
            protection_ans = np.dot(query_workload, syno_eigen[key])

            real_ans = compute_real_query(orig_query_primary_no_sub[i])
            # print(key,orig_query_primary_no_sub[i],protection_ans,real_ans)
            # print(orig_query_primary_no_sub[i],protection_ans,real_ans)
            view_original_list.append((key[0], views_information[key]))
            query_list.append(orig_query_primary_no_sub[i])
            real_ans_list.append(real_ans)
            privacy_ans_list.append(protection_ans)
            # print(orig_query_primary_no_sub[i], protection_ans)
        except (TypeError, KeyError):
            print(orig_query_primary_no_sub[i], "!")
    return view_original_list, query_list, real_ans_list, privacy_ans_list


def compute_real_query(query):
    conn = psycopg2.connect(database='tpc-h-10', user="postgres", password="root", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result[0][0]


def workload_vect(view_workload, df_view_vect_list):
    view_workload_vect = OrderedDict()
    for i in view_workload.keys():
        view_workload_vect[i] = []

    for i, ikey in enumerate(view_workload.keys()):
        query_list = view_workload[ikey]
        df_view = df_view_vect_list[i]
        for query in query_list:

            df_sign = df_view.copy()
            columns = df_sign.columns
            new_columns = {columns[-1]: 'sign'}
            df_sign = df_sign.rename(columns=new_columns)
            df_sign = df_sign.applymap(lambda x: True)

            try:
                statement = sqlparse.parse(query)[0]
                query_where = get_query_where(statement.tokens)
                for sub in query_where.get_sublists():
                    sub_list = get_token_list_name(sub.tokens)
                    for itwo, two in enumerate(sub_list):
                        if (two == '='):
                            sub_list[itwo] = '=='
                    evall = 'x' + ''.join(sub_list[1:])
                    df_sign[sub_list[0]] = df_view[sub_list[0]].apply(lambda x: True if eval(evall) else False)
            except ValueError:
                pass
            df_sign['sign'] = df_sign.iloc[:, :-1].all(axis=1)
            df_sign['sign'] = df_sign['sign'].replace({True: 1, False: 0})
            query_workload = list(df_sign.iloc[:, -1])
            view_workload_vect[ikey].append(query_workload)
    return view_workload_vect


def pickle_read(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data


if __name__ == "__main__":
    pass_queries_path = ['../../dataQuery/tpch/query/pass_analysis_queries.sql']
    view_df_path = '../../synopsis/tpch/real/view_df.pkl'
    syno_workload_path = '../../synopsis/tpch/protection/workload/syno_workload.pkl'
    syno_eigen_path = '../../synopsis/tpch/protection/eigen/syno_eigen.pkl'
    syno_eigen_non_negative_path = '../../synopsis/tpch/protection/eigen/syno_eigen_non_negative.pkl'
    views_information_path = '../../views/tpch/views_information.pkl'
    file_query_response(pass_queries_path, view_df_path, syno_eigen_path, views_information_path)
