import sqlparse

from utilsConvert import get_sub_query, get_token_list_type, update_tokenlist


def unrelated_control(tokenlist):
    if unrelated_is_agg(tokenlist.tokens):
        primary_sub_list = unrelated_sub_agg_convert_rule_2_2_1(tokenlist)
    else:
        pass
    return primary_sub_list


def unrelated_sub_agg_convert_rule_2_2_1(tokenlist):
    sub_query = get_sub_query(tokenlist.tokens)
    replace_tokens = sqlparse.parse("'sub_query'")[0].tokens
    sub_token_list = sqlparse.sql.TokenList(sub_query.tokens[1:-1])
    sub_query.tokens = replace_tokens
    update_tokenlist(sub_token_list)
    update_tokenlist(tokenlist)
    primary_sub_list = [sub_token_list, tokenlist]
    return primary_sub_list


def unrelated_is_agg(tokens):
    sub_query = get_sub_query(tokens)
    sub_token_list_type = get_token_list_type(sub_query.tokens)
    if 'Function' in sub_token_list_type:
        return True
    else:
        return False
