import pickle
import sqlparse
import pandas as pd
from utilsConvert import get_token_list_type, get_query_where, get_token_list_name
import psycopg2
from collections import OrderedDict
from queryTruncationFreeJoin import main_query_LP_truncation_free_join
from ExtractInfo import mainExtractInfo


def main_vectorization(views_path, view_to_linkQuery_path, view_to_noLinkQuery_path, view_tau_path, view_vect_dict_path,
                       view_workload_vect_dict_path, view_df_path, primary_path, key_path, query_path, out_info_path):
    views = readpickle(views_path)
    view_to_linkQuery = readpickle(view_to_linkQuery_path)
    view_to_noLinkQuery = readpickle(view_to_noLinkQuery_path)
    # print(views)
    # print(view_to_linkQuery)
    # print(view_to_noLinkQuery)
    view_vect_list, df_view_vect_list, view_vect_dict = view_vectorize(views)

    view_workload = get_view_workload(views, view_to_linkQuery, view_to_noLinkQuery)
    view_workload_vect_dict = workload_vect(view_workload, df_view_vect_list, view_vect_list)
    view_df_dict = get_view_df(views, df_view_vect_list)
    view_tau = get_view_tau(views)
    view_query_free_filter = get_view_query_free_filter(views)
    view_df_dict, view_vect_dict = get_after_truncate_free_self_join(view_tau, view_df_dict, view_query_free_filter,
                                                                     primary_path, key_path, query_path, out_info_path)
    # print(view_df)
    writepickle(view_tau_path, view_tau)
    writepickle(view_vect_dict_path, view_vect_dict)
    writepickle(view_workload_vect_dict_path, view_workload_vect_dict)
    writepickle(view_df_path, view_df_dict)
    for i in view_df_dict.keys():
        print(i)
        print(view_df_dict[i])
    # print(view_df)
    # view_vect_print(view_vect_dict,view_workload_vect_dict)


def get_after_truncate_free_self_join(view_tau, view_df, view_query_free_filter, primary_path, key_path, query_path,
                                      out_info_path):
    view_vect = OrderedDict()
    for key in view_df.keys():
        tau = view_tau[key]
        if tau is None:
            pass
        else:
            query_free = view_query_free_filter[key]
            # print(query_free)
            df = view_df[key]
            # print(df.columns)
            # print(query_free_filter)
            for index, row in df.iterrows():
                query_free_filter = query_free
                row_dict = dict(row[:-1])
                kv_list = [f"{k}='{v}'" for k, v in row_dict.items()]
                filter_str = ' AND '.join(kv_list)
                if 'WHERE' in query_free_filter.upper():
                    query_free_filter = query_free_filter[:-1] + ' AND ' + filter_str + ';'
                else:
                    query_free_filter = query_free_filter[:-1] + ' WHERE ' + filter_str + ';'

                with open(query_path, 'w') as file:
                    file.write(query_free_filter)
                mainExtractInfo(
                    ['-D', 'tpc-h-10', '-Q', query_path, '-P', primary_path, '-K', key_path, '-O', out_info_path])
                Q_tau = main_query_LP_truncation_free_join(['-I', out_info_path, '-T', tau])
                view_df[key].iloc[index, -1] = Q_tau
        view_vect[key] = list(view_df[key].iloc[:, -1])
    return view_df, view_vect


def get_view_query_free_filter(views):
    view_query_free_filter = OrderedDict()
    for i, view in enumerate(views):
        key = (view[0], view[1])
        view_query_free_filter[key] = view[3]
    return view_query_free_filter


def get_view_df(views, df_view_vect_list):
    view_df = OrderedDict()
    for i, view in enumerate(views):
        key = (view[0], view[1])
        view_df[key] = df_view_vect_list[i]
    return view_df


def get_view_tau(views):
    view_tau = OrderedDict()
    for i, view in enumerate(views):
        key = (view[0], view[1])
        view_tau[key] = view[5]
    return view_tau


def view_vect_print(view_vect_dict, view_workload_vect_dict):
    print(view_vect_dict.keys())
    print(view_workload_vect_dict.keys())
    for key in view_vect_dict.keys():
        view_vect = view_vect_dict[key]
        workload_vect_list = view_workload_vect_dict[key]
        for va in workload_vect_list:
            print(len(view_vect), len(va))
            # print(view_vect)
            # print(va)


def workload_vect(view_workload, df_view_vect_list, view_vect_list):
    view_workload_vect = OrderedDict()
    for i in view_workload.keys():  #
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


def get_view_workload(views, view_to_linkQuery, view_to_noLinkQuery):
    view_workload = OrderedDict()
    for view in views:
        tu = (view[0], view[1])
        view_workload[tu] = []
    for primary_sub in view_to_linkQuery:
        primary = primary_sub[0]
        tu = (primary[0], primary[1])
        view_workload[tu].append(primary[2])
        sub_query_result = compute_real_query(primary[3])
        sub = primary_sub[1]
        tu = (sub[0], sub[1])
        add_sub = sub[2].replace("'sub_query'", str(sub_query_result))
        view_workload[tu].append(add_sub)

    for view_query in view_to_noLinkQuery:
        tu = (view_query[0], view_query[1])
        view_workload[tu].append(view_query[2])
    return view_workload


def compute_real_query(query):
    conn = psycopg2.connect(database='tpc-h-10', user="postgres", password="root", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result[0][0]


def view_vectorize(views):
    view_vect_dict = OrderedDict()
    view_vect_list = []
    df_view_vect_list = []
    for i, view in enumerate(views):
        key = (view[0], view[1])
        statement = sqlparse.parse(view[2])[0]
        statement_list_type = get_token_list_type(statement.tokens)
        select_index = statement_list_type.index('DML')
        attr = statement.token_next(select_index)[1]
        attr_index = statement.token_index(attr)
        repalce_atrr = sqlparse.parse(str(attr) + "," + view[0])[0]
        statement.tokens[attr_index] = repalce_atrr
        statement_str = str(statement)
        end_index = statement_str.index(';')
        view_vect_query = statement_str[:end_index] + " GROUP BY " + str(attr) + ';'
        view_vect, df_view_vect = pd_execute_view_vect_query(view_vect_query, str(repalce_atrr))
        # print(view_vect_query)
        # print(df_view_vect)
        view_vect_list.append(view_vect)
        df_view_vect_list.append(df_view_vect)
        view_vect_dict[key] = view_vect

    return view_vect_list, df_view_vect_list, view_vect_dict


# def execute_view_vect_query(query):
#     conn = psycopg2.connect(database='tpc-h-10', user="postgres", password="root", host="localhost",port="5432")
#     cur = conn.cursor()
#     cur.execute(query)
#     col_names = [desc[0] for desc in cur.description]
#     print(col_names)
#     result = cur.fetchall()
#     cur.close()
#     conn.close()
#     print(result[0])
#     return result[0][0]

def pd_execute_view_vect_query(query, replace_atrr):
    conn = psycopg2.connect(database='tpc-h-10', user="postgres", password="root", host="localhost", port="5432")
    df = pd.read_sql(query, con=conn)
    df.columns = replace_atrr.split(',')
    view_vect = list(df.iloc[:, -1])
    conn.close()
    return view_vect, df


def writepickle(path, data):
    with open(path, 'wb') as file:
        pickle.dump(data, file)


def readpickle(path):
    with open(path, 'rb') as f:
        loaded_data = pickle.load(f)
    return loaded_data


if __name__ == "__main__":
    views_path = '../../views/tpch/views_information.pkl'
    view_to_linkQuery_path = '../../views/tpch/view_to_linkQuery.pkl'
    view_to_noLinkQuery_path = '../../views/tpch/view_to_noLinkQuery.pkl'
    view_tau_path = '../../views/tpch/view_tau.pkl'
    view_vect_dict_path = '../../synopsis/tpch/real/syno_vect_dict.pkl'
    view_workload_vect_dict_path = '../../views/tpch/view_workload_vect_dict.pkl'
    view_df_path = '../../synopsis/tpch/real/view_df.pkl'
    key_path = '../../basic/primary_key.txt'
    query_path = '../../information/tpch/noFilter/agg_no_filter_database_view_query.txt'
    out_info_path = '../../information/tpch/noFilter/out_info.txt'
    primary_path = '../../basic/primary_relation.txt'
    main_vectorization(views_path, view_to_linkQuery_path, view_to_noLinkQuery_path, view_tau_path, view_vect_dict_path,
                       view_workload_vect_dict_path, view_df_path, primary_path, key_path, query_path, out_info_path)
    # pd_execute_view_vect_query('SELECT ccredit,cname,cpno,count(*) FROM course,sc WHERE course.cno = sc.cno GROUP BY ccredit,cname,cpno;')
