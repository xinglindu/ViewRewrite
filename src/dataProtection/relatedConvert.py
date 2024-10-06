import sqlparse
from utilsConvert import get_sub_query, get_token_list_type, update_tokenlist, get_query_where, \
    get_primary_query_relation


def related_control(tokenlist):
    if related_is_agg(tokenlist.tokens):
        related_agg_convert_rule_1_1_1(tokenlist)
    else:
        pass


def related_agg_convert_rule_1_1_1(tokenlist):
    sub_query = get_sub_query(tokenlist.tokens)
    sub_query_list_type = get_token_list_type(sub_query.tokens)

    sub_query_relation = get_primary_query_relation(sub_query.tokens)
    sub_query_relation_str = str(sub_query_relation)

    sub_query_fct_index = sub_query_list_type.index('Function')
    sub_query_fct = sub_query[sub_query_fct_index]

    sub_query_where = get_query_where(sub_query.tokens)
    sub_query_where_str = str(sub_query_where)
    for i in sub_query_where.get_sublists():
        for j in i.get_sublists():
            j_str = str(j)
            if (sub_query_relation_str in j_str):
                sub_key = j[2]
                break

    grby = '(select ' + str(sub_key) + ', ' + str(sub_query_fct) + ' agg ' + 'from ' + str(
        sub_query_relation) + ' group by ' + str(sub_key) + ')'
    convert_query = ''
    query_list_type = get_token_list_type(tokenlist.tokens)

    where_index = query_list_type.index('Where')
    ttop = tokenlist[:where_index]
    ttop_str = ''
    for i in ttop:
        ttop_str += str(i)

    query_where = get_query_where(tokenlist.tokens)
    query_where_str = str(query_where)
    query_where_sublist = query_where.get_sublists()
    filter_list = []
    for i, v in enumerate(query_where_sublist):
        if (i != 0):
            filter_list.append(str(v))
    join_str = sub_query_where_str.replace(sub_query_relation_str, 'tt')
    convert_filter = query_where_str.replace(str(sub_query), 'agg').replace('WHERE', ' AND')
    convert_query += ttop_str + ',' + grby + ' tt ' + join_str + convert_filter
    tokenlist.tokens = sqlparse.parse(convert_query)[0].tokens
    update_tokenlist(tokenlist)


def related_is_agg(tokens):
    sub_query = get_sub_query(tokens)
    sub_token_list_type = get_token_list_type(sub_query.tokens)
    if 'Function' in sub_token_list_type:
        return True
    else:
        return False
