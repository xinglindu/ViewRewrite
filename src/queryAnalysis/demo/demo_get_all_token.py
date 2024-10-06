import sqlparse


def print_tokens(token):
    if isinstance(token, sqlparse.sql.TokenList):
        for sub_token in token:
            print_tokens(sub_token)
    else:
        print(token.ttype, token)


sql = ""
parsed = sqlparse.parse(sql)[0]

# Recursively print all tokens
print_tokens(parsed)
