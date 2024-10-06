import sqlparse
from utilsConvert import get_all_name_relation, get_sub_query_where_relations, get_sub_query, \
    get_primary_query_relation, get_token_list_type
from derivedConvert import derived_control
from unrelatedConvert import unrelated_control
from relatedConvert import related_control


def control_convert(filename):
    format_queries = read_sql_file(filename)
    parsedes = sqlparse.parse(format_queries)
    primary_no_sub_list = []
    primary_sub_list_list = []
    for parsed in parsedes:
        tokenlist = sqlparse.sql.TokenList(parsed.tokens)
        if (check_is_nested_query(tokenlist.tokens)):
            if check_is_related(tokenlist.tokens):
                related_control(tokenlist)
        if (check_is_nested_query(tokenlist.tokens)):
            if not check_is_related(tokenlist.tokens):
                primary_sub_list = unrelated_control(tokenlist)
                primary_sub_list_list.append(primary_sub_list)
        if check_is_derived_table(tokenlist.tokens):
            derived_control(tokenlist)
        if not check_is_primay_sub_query(tokenlist):
            primary_no_sub_list.append(tokenlist)
    return primary_no_sub_list, primary_sub_list_list


def access_get_orig(filename):
    format_queries = read_sql_file(filename)
    parsedes = sqlparse.parse(format_queries)
    primary_no_sub_list = []
    primary_sub_list_list = []
    for parsed in parsedes:
        ori_query = str(parsed)
        tokenlist = sqlparse.sql.TokenList(parsed.tokens)
        if (check_is_nested_query(tokenlist.tokens)):
            if check_is_related(tokenlist.tokens):
                related_control(tokenlist)
        if (check_is_nested_query(tokenlist.tokens)):
            if not check_is_related(tokenlist.tokens):
                primary_sub_list = unrelated_control(tokenlist)
                primary_sub_list_list.append(ori_query)
        if check_is_derived_table(tokenlist.tokens):
            derived_control(tokenlist)
        if not check_is_primay_sub_query(tokenlist):
            primary_no_sub_list.append(ori_query)
    return primary_no_sub_list, primary_sub_list_list


def check_is_primay_sub_query(tokenlist):
    tokenlist_str = str(tokenlist)
    if "sub_query" in tokenlist_str:
        return True
    else:
        return False


def check_is_derived_table(tokens):
    token_list_type = get_token_list_type(tokens)
    if "CTE" in token_list_type:
        return True
    primay_Identifier_relation = get_primary_query_relation(tokens)
    token_list_type = get_token_list_type(primay_Identifier_relation.tokens)
    if "Parenthesis" in token_list_type:
        return True
    for i in primay_Identifier_relation.get_sublists():
        token_list_type_i = get_token_list_type(i.tokens)
        if "Parenthesis" in token_list_type_i:
            return True
    return False


def check_is_nested_query(tokens):
    try:
        sub_query = get_sub_query(tokens)
    except ValueError:
        return False
    if sub_query is None:
        return False
    else:
        return True


def check_is_related(tokens):
    try:
        all_name_relation = set(get_all_name_relation(tokens))
        sub_query_where_relations = set(get_sub_query_where_relations(tokens))
    except AttributeError:
        return False
    except ValueError:
        return False
    if all_name_relation and sub_query_where_relations:
        return True
    else:
        return False


def read_sql_file(filename):
    with open(filename, "r") as f:
        queries = f.read()
        format_queries = sqlparse.format(queries, keyword_case="upper", identifier_case="lower", strip_comments=True,
                                         use_space_around_operators=True)
        return format_queries


if __name__ == "__main__":
    control_convert("../../dataQuery/tpch/query/original_query/all/count.sql")
    control_convert("../../dataQuery/tpch/query/original_query/all/sum.sql")
