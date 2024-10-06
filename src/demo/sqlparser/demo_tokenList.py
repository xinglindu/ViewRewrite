import sqlparse

query = "SELECT column1, column2 FROM table1 WHERE column1 = 'value'"
parsed = sqlparse.parse(query)[0]
tokens = parsed.tokens
print(parsed._get_repr_name(), parsed.tokens)
tokenlist = sqlparse.sql.TokenList(tokens)
print(tokenlist._get_repr_name(), tokenlist)
print(tokenlist._pprint_tree())
print([i for i in tokenlist.flatten()])
print([i for i in tokenlist.get_sublists()])
print(tokenlist.token_next(0))
print(tokenlist.get_token_at_offset(5))
print(tokenlist.token_first())
print(tokenlist.token_prev(1))
print(tokenlist.token_next(1))
print(tokenlist.get_alias())
print(tokenlist.get_name())
print(tokenlist.get_real_name())
statment = sqlparse.sql.Statement(tokenlist)
print(statment._get_repr_name())
print(tokenlist.tokens)
