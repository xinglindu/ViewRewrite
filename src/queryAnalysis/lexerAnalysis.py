import sqlparse
from pygments.lexers import SqlLexer
from pygments.token import Error


def lexerCheck(sql):
    sql_without_comments = sqlparse.format(sql, strip_comments=True)
    # print(sql_without_comments)
    return_query = sqlparse.format(sql, keyword_case="upper", identifier_case="lower", strip_comments=True,
                                   use_space_around_operators=True)
    tokens = sqlparse.parse(sql_without_comments)[0].tokens
    # for token in tokens:
    #     print(f"Token type: {token.ttype}, value: {token.value}")

    formatted_sql = sqlparse.format(sql_without_comments, reindent=True)
    # print(formatted_sql)

    normalized_sql = sqlparse.format(formatted_sql, keyword_case='upper', identifier_case='lower')

    lexer = SqlLexer()
    has_errors = False
    for token_type, value in lexer.get_tokens(sql):
        if token_type == Error:
            has_errors = True
            return "Lexical error!"
    if not has_errors:
        return return_query


if __name__ == "__main__":
    lexerResult = lexerCheck("SELECT * FROM mytable WHERE id = 1")
    print("lexerAnalysis\n", lexerResult, "\n")
