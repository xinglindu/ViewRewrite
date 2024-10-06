import sqlparse
import re


def get_format_query_tokens(query):
    format_query = sqlparse.format(query, keyword_case="upper", identifier_case="lower", strip_comments=True,
                                   use_space_around_operators=True)
    parsed = sqlparse.parse(format_query)[0]
    tokens = sqlparse.sql.TokenList(parsed.tokens).tokens
    return tokens


def update_tokenlist(tokenlist):
    no_new_line_str = (str(tokenlist)).replace("\n", '')
    no_new_line_str_one_space = re.sub(' +', ' ', no_new_line_str).strip()
    format_tokens = get_format_query_tokens(no_new_line_str_one_space)
    tokenlist.tokens = format_tokens


def group_tokens(tokenlist_class, re_tokens, start, end):
    tokenlist_class.tokens[start:end] = re_tokens
    for token in re_tokens:
        token.parent = tokenlist_class


# def replace_tokenlist(self_tokens,re_tokens,start,end):
#     self_tokens[start:end] = re_tokens
#     token_list = sqlparse.sql.TokenList(self_tokens)
#     for token in re_tokens:
#         token.parent = token_list
#     return token_list
def get_token_list_type(tokens):
    tokens_str = str(tokens)[1:-1]
    token_list = tokens_str.split(">,")
    token_list_type = []
    for token in token_list:
        tt = token.split()[0][1:]
        token_list_type.append(tt)
    return token_list_type


def get_token_list_name(tokens):
    token_list = []
    for i in tokens:
        token_list.append(str(i))
    return token_list


def get_FROM_index(tokens):
    for i, token in enumerate(tokens):
        token_str = str(token)
        if token_str == 'FROM':
            return i


def get_primary_query_relation(tokens):
    from_index = get_FROM_index(tokens)
    tokenlist = sqlparse.sql.TokenList(tokens)
    primary_query_relation = tokenlist.token_next(from_index)
    primay_Identifier_relation = primary_query_relation[1]
    return primay_Identifier_relation


def get_all_name_relation(tokens):
    primay_Identifier_relation = get_primary_query_relation(tokens)
    primay_tokens_relation = primay_Identifier_relation.tokens
    tokenlist = sqlparse.sql.TokenList(primay_tokens_relation)
    name_list_token = []

    for i in primay_tokens_relation:
        if (str(i.ttype) == 'Token.Name'):
            name_list_token.append(i)

    for i in tokenlist.get_sublists():
        for j in i.tokens:
            if (str(j.ttype) == 'Token.Name'):
                name_list_token.append(j)
            elif str(j.ttype) == 'None':
                for k in j.tokens:
                    if (str(k.ttype) == 'Token.Name'):
                        name_list_token.append(k)
    return get_token_list_name(name_list_token)


def get_query_where(tokens):
    token_list_type = get_token_list_type(tokens)
    where_index = token_list_type.index('Where')
    token_list = sqlparse.sql.TokenList(tokens)
    query_where = token_list.token_next(where_index - 1)[1]
    return query_where


def get_sub_query(tokens):
    query_where = get_query_where(tokens)
    for i in query_where.get_sublists():
        token_list_type = get_token_list_type(i.tokens)
        for index, token_type in enumerate(token_list_type):
            if token_type == 'Parenthesis':
                return i.tokens[index]
    token_list_type = get_token_list_type(query_where.tokens)
    for index, token_type in enumerate(token_list_type):
        if token_type == 'Parenthesis':
            return query_where.tokens[index]


def get_sub_query_where_relations(tokens):
    relations = []
    sub_query = get_sub_query(tokens)
    sub_query_where = get_query_where(sub_query.tokens)
    for i in sub_query_where.get_sublists():
        for j in i.get_sublists():
            if len(j.tokens) == 3:
                relations.append(j.tokens[0])
    return get_token_list_name(relations)


if __name__ == "__main__":
    query = "SELECT Sno FROM SC WHERE Cno=1;"
    tokens = get_format_query_tokens(query)
    token_list = sqlparse.sql.TokenList(tokens)
    group_tokens(token_list, get_format_query_tokens("and c=1"), 2, 4)
    print(token_list)
