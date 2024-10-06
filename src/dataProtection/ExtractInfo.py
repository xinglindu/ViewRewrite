# -*- coding: utf-8 -*-
import getopt
import psycopg2
import sys
from utilsConvert import get_FROM_index, get_primary_query_relation, get_token_list_type
import sqlparse


def ReadQuery():
    global query
    global query_path
    query = ""
    query_file = open(query_path, 'r')
    # Read the query file and store in query
    for line in query_file.readlines():
        query = query + line
        if ";" in query:
            query = query.replace('\n', " ")
            break


def ReadPrimaryRelation():
    global private_relation_path
    global primary_relation_list
    primary_relation_list = []
    input_file = open(private_relation_path, 'r')
    for line in input_file.readlines():
        line = line.replace('\n', "")
        primary_relation_list.append(line)


def ReadPrimaryKey():
    global key_path
    global key_list
    global primary_relation_list
    key_list = {}
    input_file = open(key_path, 'r')
    i = 0
    for line in input_file.readlines():
        line = line.replace('\n', "")
        elements = line.split()
        key_list[primary_relation_list[i]] = elements
        i += 1


def RewriteQuery():
    global query
    global rewrite_query
    global key_list
    global primary_relation_list
    global colum_num

    # Split the query into select, from and where clauses
    # Match the corresponding terms
    from_string = ""
    select_string = ""
    where_string = ""
    query_t = query.replace(",", " ")
    words = query_t.split(" ")

    for word in words:
        if word.lower() == "select":
            select_string = word
        if word.lower() == "from":
            from_string = word
        if word.lower() == "where":
            where_string = word

    parser_string = query
    parser_string = parser_string.replace(select_string + " ", "")
    parser_string = parser_string.replace(from_string + " ", "\n")
    parser_string = parser_string.replace(where_string + " ", "\n")
    parser_string = parser_string.replace(";", "")
    parser_strings = parser_string.split("\n")
    select_strings = parser_strings[0]
    from_strings = parser_strings[1]
    where_strings = parser_strings[2]

    # Split the select attributes
    select_strings = select_strings.replace(",", "\n")
    select_strings = select_strings.split("\n")
    # Split the relations
    relations_strings = from_strings.replace(",", "\n")
    relations_strings = relations_strings.split("\n")

    # Renaming_private_relations stores all the relations that are private
    renaming_private_relations = {}
    for primary_relation in primary_relation_list:
        renaming_private_relations[primary_relation] = []

    # Go through the relations in the from clause
    for relations_string in relations_strings:
        relations_string = relations_string.split()
        origin_relation = relations_string[0]
        # Case 1: there is a renaming, xxx as xxx
        if len(relations_string) > 1:
            renaming_relation = relations_string[-1]
        # Case 2: there is no renaming
        else:
            renaming_relation = relations_string[0]
        if origin_relation in primary_relation_list:
            renaming_private_relations[origin_relation].append(renaming_relation)

    # Rewrite the query
    rewrite_query = "select "
    # Case 1: aggregation query
    if "sum" in select_strings[0]:
        if " as " in select_strings[0]:
            select_strings[0] = select_strings[0].replace(" as ", "\n").split("\n")[0]
        rewrite_query = rewrite_query + select_strings[0][
                                        select_strings[0].find('(') + 1: select_strings[0].rfind(')')] + ", "
    # Case 2: counting query
    else:
        rewrite_query = rewrite_query + "1, "

    select_part = ""
    i = 0
    colum_num = 0
    # Go through all the private relations
    for primary_relation in primary_relation_list:
        for renaming_name in renaming_private_relations[primary_relation]:
            colum_num += 1
            if i > 0:
                select_part = select_part + ", "
            select_part = select_part + "'" + primary_relation + "'"
            for key in key_list[primary_relation]:
                select_part = select_part + "||concat(" + renaming_name + "." + key + ",\',\')"
            select_part = select_part + " as id" + str(i)
            i += 1
    parsedd = sqlparse.parse(query)[0]
    if check_is_derived_table(parsedd.tokens):
        colum_num = 1
        top_part = "'" + primary_relation + "'"
        for key in key_list[primary_relation]:
            top_part = top_part + "||concat(" + primary_relation + "." + key + ",\',\')"
        top_part = top_part + " as id"
        from_index = get_FROM_index(parsedd.tokens)
        from_query = parsedd[from_index:]
        from_query_str = ''
        for i in from_query:
            from_query_str += str(i)
        rewrite_query = rewrite_query + " " + top_part + " " + from_query_str

    else:
        rewrite_query = rewrite_query + " " + select_part + " from " + from_strings + " where " + where_strings + ";"


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


def ExtractRelationship():
    global database_name
    global rewrite_query
    global output_path
    global renaming_private_relations
    global colum_num
    con = psycopg2.connect(database=database_name, user="postgres", password="root", host="localhost", port="5432")
    cur = con.cursor()
    # Run the query and get the results
    cur.execute(rewrite_query)
    res = cur.fetchall()
    id_dic = {}
    results = open(output_path, 'w')
    num_id = 0
    # Go through the results
    for i in range(len(res)):
        temp_res = res[i]
        # Write the count/aggregation result
        results.write(str(temp_res[0]) + " ")
        # Write the private relations in the result
        for j in range(1, colum_num + 1):
            temp_id = temp_res[j]
            # Reordering the private relations
            if temp_id in id_dic:
                results.write(str(id_dic[temp_id]) + " ")
            else:
                id_dic[temp_id] = num_id
                results.write(str(num_id) + " ")
                num_id += 1
        results.write("\n")
    con.commit()
    con.close()


def mainExtractInfo(argv):
    # Name of the database to be queried
    global database_name
    # Path of the txt file storing the query
    global query_path
    # Path of file of the private relation
    global private_relation_path
    # Path of the file of primary keys
    global key_path
    # Path of the output file of the query results
    global output_path
    try:
        opts, args = getopt.getopt(argv, "h:D:Q:P:K:O:",
                                   ["Database=", "QueryPath=", "PrivateRelationPath=", "KetPath", "Output="])
    except getopt.GetoptError:
        print(
            "SystemExtractInfo.py -D <database name> -Q <query file path> -P <private relation path> -K <primary key path> -O <output file>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(
                "SystemExtractInfo.py -D <database name> -Q <query file path> -P <private relation path> -K <primary key path> -O <output file>")
            sys.exit()
        elif opt in ("-D", "--Database"):
            database_name = arg
        elif opt in ("-Q", "--QueryPath"):
            query_path = arg
        elif opt in ("-P", "--PrivateRelationPath"):
            private_relation_path = arg
        elif opt in ("-K", "--KeyPath"):
            key_path = arg
        elif opt in ("-O", "--Output"):
            output_path = arg
    ReadQuery()
    ReadPrimaryRelation()
    ReadPrimaryKey()
    RewriteQuery()
    ExtractRelationship()


if __name__ == "__main__":
    # main(sys.argv[1:])
    mainExtractInfo(['-D', 'tpch', '-Q', '../../basic/tpch/noFilter/agg_no_filter_database_view_query.txt', '-P',
                     '../../basic/tpch/primary_relation.txt', '-K', '../../basic/tpch/primary_key.txt', '-O',
                     '../../basic/tpch/noFilter/out_info.txt'])
