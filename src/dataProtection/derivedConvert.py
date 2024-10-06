import sqlparse
from utilsConvert import get_token_list_type, get_primary_query_relation, get_token_list_name, get_query_where, \
    update_tokenlist, get_FROM_index


def derived_control(tokenlist):
    if derived_is_with(tokenlist.tokens):
        derived_with_convert_rule_3_4(tokenlist)
    if derived_is_group(tokenlist.tokens):
        pass
    else:
        derived_no_group_by_convert_rule_3_1(tokenlist)
        # print(tokenlist)


def derived_no_group_by_convert_rule_3_1(tokenlist):
    primary_query_relation = get_primary_query_relation(tokenlist.tokens)
    primary_query_relation_token_list = get_token_list_type(primary_query_relation.tokens)
    if 'Parenthesis' in primary_query_relation_token_list:
        parenthesis_index = primary_query_relation_token_list.index('Parenthesis')
        derived_query = primary_query_relation.tokens[parenthesis_index]
        sub_query_relation = get_primary_query_relation(derived_query.tokens)
        sub_query_relation_list_type = get_token_list_type(sub_query_relation.tokens)
        if "Name" in sub_query_relation_list_type:
            try:
                sub_where = get_query_where(derived_query.tokens)
                for i in primary_query_relation.get_sublists():
                    if len(i.tokens) == 1:
                        rename = i
                for i in sub_where.get_sublists():
                    for j in i.get_sublists():
                        add_name_tokens = sqlparse.parse(str(rename) + ".")[0].tokens[0].tokens
                        add_name_tokens.extend(j.tokens)
                        j.tokens = add_name_tokens
                try:
                    primary_where = get_query_where(tokenlist.tokens)
                    add_name_tokens = sqlparse.parse(str(sub_where) + " AND")[0].tokens[0].tokens[1:]
                    primary_where.tokens = primary_where.tokens[0:1] + add_name_tokens + primary_where[1:]
                    derived_query.tokens = sub_query_relation.tokens
                    # print(tokenlist)
                except:
                    index_from = get_FROM_index(tokenlist.tokens)
                    token_primary_relation = tokenlist.token_next(index_from)[1]
                    index_primary_realtion = tokenlist.token_index(token_primary_relation)
                    add_name_tokens = sqlparse.parse(" " + str(sub_where))[0]
                    tokenlist.insert_after(index_primary_realtion, add_name_tokens)
                    derived_query.tokens = sub_query_relation.tokens
                    # print(tokenlist)
            except:
                derived_query.tokens = sub_query_relation.tokens
                # print(tokenlist)
        else:
            pass
    else:
        for i in primary_query_relation.get_sublists():
            primary_query_relation_token_list = get_token_list_type(i.tokens)
            if 'Parenthesis' in primary_query_relation_token_list:  #
                parenthesis_index = primary_query_relation_token_list.index('Parenthesis')
                derived_query = i.tokens[parenthesis_index]
                sub_query_relation = get_primary_query_relation(derived_query.tokens)
                sub_query_relation_list_type = get_token_list_type(sub_query_relation.tokens)
                if "Name" in sub_query_relation_list_type:
                    try:
                        sub_where = get_query_where(derived_query.tokens)
                        for i in i.get_sublists():
                            if len(i.tokens) == 1:
                                rename = i
                        for i in sub_where.get_sublists():
                            for j in i.get_sublists():
                                add_name_tokens = sqlparse.parse(str(rename) + ".")[0].tokens[0].tokens
                                add_name_tokens.extend(j.tokens)
                                j.tokens = add_name_tokens
                        try:
                            primary_where = get_query_where(tokenlist.tokens)
                            add_name_tokens = sqlparse.parse(str(sub_where) + " AND")[0].tokens[0].tokens[1:]
                            primary_where.tokens = primary_where.tokens[0:1] + add_name_tokens + primary_where[1:]
                            derived_query.tokens = sub_query_relation.tokens
                            # print(tokenlist)
                        except:
                            index_from = get_FROM_index(tokenlist.tokens)
                            token_primary_relation = tokenlist.token_next(index_from)[1]
                            index_primary_realtion = tokenlist.token_index(token_primary_relation)
                            add_name_tokens = sqlparse.parse(" " + str(sub_where))[0]
                            tokenlist.insert_after(index_primary_realtion, add_name_tokens)
                            derived_query.tokens = sub_query_relation.tokens
                            # print(tokenlist)
                    except:
                        derived_query.tokens = sub_query_relation.tokens
                        # print(tokenlist)
                else:
                    pass
    update_tokenlist(tokenlist)


def derived_with_convert_rule_3_4(tokenslist):
    # print(tokenslist.tokens)
    token_list_type = get_token_list_type(tokenslist.tokens)
    index_with = token_list_type.index("CTE")
    original_replace_Identifier = tokenslist.token_next(index_with)[1]
    # print(original_replace_tokens.tokens)
    replace_token_list_type = get_token_list_type(original_replace_Identifier.tokens)
    replace_name_index = replace_token_list_type.index("Name")
    replace_name = str(original_replace_Identifier.tokens[replace_name_index])
    # print(replace_name)
    replace_parenthesis_index = replace_token_list_type.index("Parenthesis")
    tmp = original_replace_Identifier.tokens[replace_name_index]
    original_replace_Identifier.tokens[replace_name_index] = original_replace_Identifier.tokens[
        replace_parenthesis_index]
    original_replace_Identifier.tokens[replace_parenthesis_index] = tmp
    primary_query_relation = get_primary_query_relation(tokenslist.tokens)
    if len(primary_query_relation.tokens) == 1:
        primary_query_relation.tokens = original_replace_Identifier.tokens
        index_DML = token_list_type.index("DML")
        tokenslist.tokens[index_with:index_DML] = []
    else:
        for i in primary_query_relation.get_sublists():
            if (str(i) == replace_name):
                i.tokens = original_replace_Identifier.tokens
        index_DML = token_list_type.index("DML")
        tokenslist.tokens[index_with:index_DML] = []
    update_tokenlist(tokenslist)


def derived_is_with(tokens):
    token_list_type = get_token_list_type(tokens)
    if "CTE" in token_list_type:
        return True


def derived_is_group(tokens):
    primary_query_relation = get_primary_query_relation(tokens)
    primary_relation_list_type = get_token_list_type(primary_query_relation.tokens)
    if "Parenthesis" in primary_relation_list_type:
        index = primary_relation_list_type.index("Parenthesis")
        list_name = get_token_list_name(primary_query_relation.tokens[index].tokens)
        for name in list_name:
            name_tmp = name.replace(" ", "")
            if ("GROUPBY" == name_tmp):
                return True
    else:
        for i in primary_query_relation.get_sublists():
            sub_relation_list_type = get_token_list_type(i.tokens)
            if "Parenthesis" in sub_relation_list_type:
                index = sub_relation_list_type.index("Parenthesis")
                list_name = get_token_list_name(i.tokens[index].tokens)
                for name in list_name:
                    name_tmp = name.replace(" ", "")
                    if ("GROUPBY" == name_tmp):
                        return True
    return False
