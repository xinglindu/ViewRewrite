import sqlparse
from viewGenerate import view_generate_main
from ExtractInfo import mainExtractInfo
from computeQueryDlsq import main_compute_query_dlsq
from utilsConvert import get_primary_query_relation, get_query_where
import psycopg2
from collections import OrderedDict


def compute_dlsq_no_filter(list_filename, primary_path, key_path, query_path, out_info_path):
    view_attr_set_list, view_primary_sub_all_list, view_primary_no_sub_all_list = view_generate_main(list_filename)
    with open(primary_path, 'r') as file:
        primary_relation = file.read()
    privacy_related_tables = get_related_tables(primary_relation)
    print(privacy_related_tables)
    for i, view_list in enumerate(view_attr_set_list):
        agg_no_filter_database_view_query = get_agg_no_filter_database_view_query(view_list[:2], privacy_related_tables,
                                                                                  primary_relation)
        view_attr_set_list[i].append(agg_no_filter_database_view_query)
        try:
            with open(query_path, 'w') as file:
                file.write(agg_no_filter_database_view_query)
            mainExtractInfo(
                ['-D', 'tpc-h-10', '-Q', query_path, '-P', primary_path, '-K', key_path, '-O', out_info_path])
            flat_view_dlsq = main_compute_query_dlsq(['-I', out_info_path])
            view_attr_set_list[i].append(flat_view_dlsq)
            # print(agg_no_filter_database_view_query,flat_view_dlsq)
        except Exception as e:
            view_attr_set_list[i].append(0)
    # print(view_attr_set_list)
    return view_attr_set_list, view_primary_sub_all_list, view_primary_no_sub_all_list


def get_agg_no_filter_database_view_query(view_agg_list, privacy_related_tables, primary_relation):
    agg_sign = view_agg_list[0]
    original_query_view = view_agg_list[1]
    agg_query = original_query_view.replace("*", agg_sign, 1)
    if "WHERE" not in agg_query:
        agg_query = agg_query[:-1] + " WHERE true;"
    if (len(privacy_related_tables) != 0) & (primary_relation not in agg_query):
        for index, related_tables in enumerate(privacy_related_tables):
            if (related_tables[0] in agg_query):
                re_privacy_related_tables = privacy_related_tables[:index + 1]
                query_statement = sqlparse.parse(agg_query)[0]
                relation_statement = get_primary_query_relation(query_statement.tokens)
                rewrite_relation_str = str(relation_statement)
                for i in re_privacy_related_tables:
                    rewrite_relation_str = rewrite_relation_str + ',' + i[2]
                relation_statement.tokens = sqlparse.parse(rewrite_relation_str)
                add_join_str = get_add_join(str(relation_statement), re_privacy_related_tables)
                where_condition = get_query_where(query_statement.tokens)
                where_condition.tokens = sqlparse.parse(str(where_condition)[:-1] + add_join_str + ';')
                return str(query_statement)
    return agg_query


def get_add_join(relation_str, privacy_related_tables):
    name_rename_relation_dict = get_name_rename_relation(relation_str)
    add_join = ''
    for i in privacy_related_tables:
        if i[0] in name_rename_relation_dict.keys():
            add_join = add_join + ' AND ' + name_rename_relation_dict[i[0]] + '.' + i[1] + ' = ' + i[2] + '.' + i[3]
        else:
            add_join = add_join + ' AND ' + i[0] + '.' + i[1] + ' = ' + i[2] + '.' + i[3]
    return add_join  #


def get_name_rename_relation(relation_str):
    relation_dict = OrderedDict()
    relation_list = relation_str.split(',')
    for i in relation_list:
        j = i.split()
        if len(j) > 1:
            relation_dict[j[0]] = j[-1]
    return relation_dict


def get_related_tables(table_name, related_tables=set(), related_tuples=[]):
    # if table_name in related_tables:
    #     return related_tuples
    related_tables.add(table_name)
    conn = psycopg2.connect(database='tpc-h-10', user="postgres", password="root", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute(f"""
        SELECT
          tc.table_name,
          kcu.column_name,
          ccu.table_name AS referenced_table_name,
          ccu.column_name AS referenced_column_name,
          tc.constraint_name
        FROM
          information_schema.table_constraints AS tc
          JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
          JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
        WHERE
          tc.constraint_type = 'FOREIGN KEY' AND ccu.table_name = '{table_name}';
    """)
    related_tuples.extend(cur.fetchall())
    # print(related_tuples)
    cur.close()
    conn.close()
    for related_tuple in related_tuples.copy():
        related_table = related_tuple[0]
        if related_table not in related_tables:
            related_tables.add(related_table)
            get_related_tables(related_table, related_tables, related_tuples)
    return related_tuples


if __name__ == "__main__":
    list_filename = ["../../dataQuery/tpch/query/original_query/base/count.sql",
                     "../../dataQuery/tpch/query/original_query/base/sum.sql"]
    primary_path = '../../basic/tpch/tpch_primary_relation.txt'
    key_path = '../../basic/tpch/tpch_key.txt'
    query_path = '../../information/tpch/noFilter/agg_no_filter_database_view_query.txt'
    out_info_path = '../../information/tpch/noFilter/out_info.txt'
    compute_dlsq_no_filter(list_filename, primary_path, key_path, query_path, out_info_path)
