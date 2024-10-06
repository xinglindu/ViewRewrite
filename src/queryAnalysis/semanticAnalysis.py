import psycopg2
import sqlparse

from lexerAnalysis import lexerCheck
from syntaxAnalysis import syntaxCheck
from toolAnalysis import getPrimaryKey, getTableFilterProperties, extract_table_names, getDependencies


def semanticCheck(syntaxSql, rawQuery):
    semanticSql = syntaxSql
    viewResolutionSql = viewResolution(semanticSql)
    if is_column_names_unique(semanticSql):
        resultIsError = semanticCheckSqlError(sql=syntaxSql)
        if "error" in resultIsError:
            return resultIsError
        else:
            resultSensitive = firstIsSensitiveField(resultIsError, rawQuery)
            return resultSensitive
    else:
        return "error: Column names are not unique."


def viewResolution(query):
    import sqlparse
    # query = "SELECT * FROM my_view WHERE id = 1"
    views = {

    }
    parsed = sqlparse.parse(query)[0]
    for token in parsed.flatten():
        if isinstance(token, sqlparse.sql.Identifier) and token.get_real_name().lower() in views:
            view_name = token.get_real_name().lower()
            view_query = views[view_name]
            view_parsed = sqlparse.parse(view_query)[0]
            tables = []
            for token in view_parsed.tokens:
                if isinstance(token, sqlparse.sql.Identifier) and token.get_real_name().lower() != view_name:
                    if len(tables) == 0 or tables[-1] != token.get_real_name().lower():
                        tables.append(token.get_real_name().lower())

            parsed.replace(token, tables[0])

    return parsed


def is_column_names_unique(sql_query):
    parsed = sqlparse.parse(sql_query)[0]

    columns = [str(token).strip() for token in parsed.tokens if str(token.ttype) == 'Name']

    return len(columns) == len(set(columns))


def semanticCheckSqlError(user="postgres", password="root", sql=""):
    conn = psycopg2.connect(database="tpc-h-10", user=user, password=password, host="localhost", port="5432")
    cur = conn.cursor()
    try:
        cur.execute(sql)
    except psycopg2.Error as e:
        return "There is an error in the sql statement:\n" + str(e)
    cur.close()
    conn.close()
    return sql


def firstIsSensitiveField(query, rawQuery):
    table_names = extract_table_names(query)
    if (len(table_names) == 1):
        tableFilterProperties = set(getTableFilterProperties(rawQuery))
        primaryKeys = set(getPrimaryKey(table_names[0]))
        diffset = primaryKeys - tableFilterProperties
        if (len(diffset) == 0):
            return "error: Involves sensitive attributes"
        else:
            return query
    else:
        table_set = set(table_names)
        foreign_table_set = set()
        for table in table_set:
            deTable = getDependencies(table)
            foreign_table_set = foreign_table_set.union(deTable)
        table_diff_set = table_set - foreign_table_set
        if len(table_diff_set) == 0:
            return query
        else:
            tableFilterProperties = set(getTableFilterProperties(rawQuery))
            primaryKeys = set()
            for table in table_diff_set:
                primaryKeys = primaryKeys.union(set(getPrimaryKey(table)))
            diffset = primaryKeys - tableFilterProperties
            if (len(diffset) == 0):
                return "error: Involves sensitive attributes"
            else:
                return query


def SecondIsSensitiveField(query):
    return query


if __name__ == "__main__":
    sql = ''
    lexerResult = lexerCheck(sql)
    if lexerResult == "Lexical error!":
        print(lexerResult)
    else:
        syntaxResult = syntaxCheck(lexerResult)
        if "error" in syntaxResult:
            print(syntaxResult)
        else:
            semanticResult = semanticCheck(syntaxResult, sql)
            print(semanticResult)
