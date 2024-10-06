import copy

import sqlparse

from controlConvert import control_convert
from utilsConvert import get_token_list_type, get_query_where, update_tokenlist, get_primary_query_relation


def view_generate_main(list_filename):
    primary_no_sub_all_list = []
    primary_sub_all_list = []
    for filename in list_filename:
        primary_no_sub_one_list, primary_sub_one_list = control_convert(filename)
        primary_no_sub_all_list.extend(primary_no_sub_one_list)
        primary_sub_all_list.extend(primary_sub_one_list)
    view_primary_no_sub_all_list, view_tmp1 = query_no_sub_view_generate(primary_no_sub_all_list)
    # for i in view_primary_no_sub_all_list:
    view_primary_sub_all_list, view_tmp2 = query_sub_view_generate(primary_sub_all_list)
    # for lists in view_primary_sub_all_list:
    view_set = view_tmp1 | view_tmp2
    view_attr_set_list = view_attribute_selection(view_set, view_primary_no_sub_all_list, view_primary_sub_all_list)
    return view_attr_set_list, view_primary_sub_all_list, view_primary_no_sub_all_list


def view_attribute_selection(view_set, view_primary_no_sub_all_list, view_primary_sub_all_list):
    view_set_list = []
    for view_agg_str in view_set:
        tmp_list = []
        tmp_list.extend(view_agg_str.split(":"))
        signal_view_selection = signal_view_attribute_selection(tmp_list[0], tmp_list[1], view_primary_no_sub_all_list,
                                                                view_primary_sub_all_list)
        tmp_list.append(signal_view_selection)
        view_set_list.append(tmp_list)
    view_set_list.sort()
    return view_set_list


def signal_view_attribute_selection(singal_sign, signal_view_str, view_primary_no_sub_all_list,
                                    view_primary_sub_all_list):
    attribute_set = set()
    for llist in view_primary_no_sub_all_list:
        sign = llist[0]
        view_str = str(llist[1])
        query_based_view = llist[2]
        if (view_str == signal_view_str) & (sign == singal_sign):
            try:
                query_where = get_query_where(query_based_view.tokens)
                for sublist in query_where.get_sublists():
                    sublist_token_type = get_token_list_type(sublist.tokens)
                    attr_index = sublist_token_type.index('Identifier')
                    attribute_set.add(str(sublist.tokens[attr_index]))
            except ValueError:
                pass
    for primary_sub_list in view_primary_sub_all_list:
        for llist in primary_sub_list:
            sign = llist[0]
            view_str = str(llist[1])
            query_based_view = llist[2]
            if (view_str == signal_view_str) & (sign == singal_sign):
                try:
                    query_where = get_query_where(query_based_view.tokens)
                    for sublist in query_where.get_sublists():
                        sublist_token_type = get_token_list_type(sublist.tokens)
                        attr_index = sublist_token_type.index('Identifier')
                        attribute_set.add(str(sublist.tokens[attr_index]))
                except ValueError:
                    pass
    attribute_set_list = list(attribute_set)
    attribute_set_list.sort()
    attribute_set_str = ",".join(attribute_set_list)
    attribute_set_statement = sqlparse.parse(attribute_set_str)[0]
    signal_view_statement = sqlparse.parse(signal_view_str)[0]
    signal_view_token_type_list = get_token_list_type(signal_view_statement.tokens)
    attribute_index = signal_view_token_type_list.index('Wildcard')
    signal_view_statement.tokens[attribute_index] = attribute_set_statement
    signal_view_tokenlist = sqlparse.sql.TokenList(signal_view_statement.tokens)
    update_tokenlist(signal_view_statement)
    # print(signal_view_tokenlist)
    # print(signal_view_str,attribute_set)
    return str(signal_view_tokenlist)


def query_sub_view_generate(primary_sub_all_list):
    view_set = set()
    view_primary_sub_all_list = []
    for primary_sub_list in primary_sub_all_list:
        view_primary_sub_list = []
        for query in primary_sub_list:
            view_list = []
            agg_sign = get_agg_sign(query.tokens)
            view_list.append(agg_sign)
            vieww = get_view(query)
            view_list.append(vieww)
            view_set.add(agg_sign + ":" + str(vieww))
            view_based_query = get_view_based_query(query)
            view_list.append(view_based_query)
            update_tokenlist(query)
            view_list.append(query)
            view_primary_sub_list.append(view_list)
        view_primary_sub_all_list.append(view_primary_sub_list)
    return view_primary_sub_all_list, view_set


def query_no_sub_view_generate(primary_no_sub_all_list):
    view_set = set()
    view_primary_no_sub_all_list = []
    for primary_no_sub in primary_no_sub_all_list:
        view_primary_no_sub_list = []
        agg_sign = get_agg_sign(primary_no_sub.tokens)
        view_primary_no_sub_list.append(agg_sign)
        view_primary = get_view(primary_no_sub)
        view_primary_no_sub_list.append(view_primary)
        view_set.add(agg_sign + ":" + str(view_primary))
        view_based_query = get_view_based_query(primary_no_sub)
        view_primary_no_sub_list.append(view_based_query)
        update_tokenlist(primary_no_sub)
        view_primary_no_sub_list.append(primary_no_sub)
        view_primary_no_sub_all_list.append(view_primary_no_sub_list)
    return view_primary_no_sub_all_list, view_set


def get_agg_sign(tokens):
    token_type_list = get_token_list_type(tokens)
    agg_index = token_type_list.index('Function')
    agg_sign = str(tokens[agg_index])
    return agg_sign


def get_view_based_query(tokenlist):
    view_based_query = sqlparse.parse(str(tokenlist))[0]
    primary_relation = get_primary_query_relation(view_based_query.tokens)
    primary_relation.tokens = sqlparse.parse("V")[0].tokens
    try:
        query_where = get_query_where(view_based_query.tokens)
        filter_list = []
        for sublist in query_where.get_sublists():
            sublist_token_type = get_token_list_type(sublist.tokens)
            if ('Single' in sublist_token_type) | ('Integer' in sublist_token_type) | ('Float' in sublist_token_type):
                filter_list.append(str(sublist))
        if len(filter_list) == 0:
            index_remove = view_based_query.token_index(query_where)
            view_based_query.tokens = view_based_query.tokens[:index_remove - 1] + view_based_query.tokens[
                                                                                   index_remove:]
            query_where.tokens = sqlparse.parse(";")[0].tokens
        else:
            query_where.tokens = sqlparse.parse("WHERE " + " AND ".join(filter_list) + ";")[0].tokens
    except ValueError:
        pass
    update_tokenlist(view_based_query)
    return view_based_query


def get_view(tokenlist):
    view_pr = sqlparse.parse(str(tokenlist))[0]
    token_type_list = get_token_list_type(view_pr.tokens)
    agg_index = token_type_list.index('Function')
    view_pr.tokens[agg_index] = sqlparse.parse("*")[0].tokens[0]
    try:
        query_where = get_query_where(view_pr.tokens)
        join_condition_list = []
        for sublist in query_where.get_sublists():
            sublist_token_type = get_token_list_type(sublist.tokens)
            if ('Single' in sublist_token_type) | ('Integer' in sublist_token_type) | ('Float' in sublist_token_type):
                pass
            else:
                join_condition_list.append(str(sublist))
        if len(join_condition_list) == 0:
            index_remove = view_pr.token_index(query_where)
            view_pr.tokens = view_pr.tokens[:index_remove - 1] + view_pr.tokens[index_remove:]
            query_where.tokens = sqlparse.parse(";")[0].tokens
        else:
            query_where.tokens = sqlparse.parse("WHERE " + " AND ".join(join_condition_list) + ";")[0].tokens
    except ValueError:
        if (token_type_list[-1] == 'Identifier'):
            view_pr.tokens.append(sqlparse.parse(';')[0])
    update_tokenlist(view_pr)
    return view_pr


if __name__ == "__main__":
    list_filename = ["../../dataQuery/tpch/query/original_query/all/count.sql",
                     "../../dataQuery/tpch/query/original_query/all/sum.sql"]
    view_generate_main(list_filename)
