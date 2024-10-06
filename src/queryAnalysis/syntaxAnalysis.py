import sqlparse
from lexerAnalysis import lexerCheck
from toolAnalysis import checkSqlError


def syntaxCheck(lexerSql):
    syntaxSql = lexerSql
    statement = sqlparse.parse(syntaxSql)[0]

    if statement.get_type() == 'SELECT':
        # print('This is a SELECT statement.')
        resultIsError = checkSqlError(syntaxSql)
        if "error" in resultIsError:
            return resultIsError
        try:
            parsed = sqlparse.parse(syntaxSql)[0]
            # print(parsed)
        except sqlparse.exceptions.SQLParseError as e:
            return "syntax error!"
        else:
            for token in parsed.tokens:
                if isinstance(token, sqlparse.sql.Function):
                    return syntaxSql
            else:
                return "This is not an aggregation query!"
    else:
        return "error: This is not a SELECT query!"


if __name__ == "__main__":
    sql = "SELECt * FROm course;"
    lexerResult = lexerCheck(sql)
    if lexerResult == "Lexical error!":
        # print(lexerResult)
        pass
    else:
        syntaxResult = syntaxCheck(lexerResult)
        if "error" in syntaxResult:
            print(syntaxResult)
        else:
            print(syntaxResult)
