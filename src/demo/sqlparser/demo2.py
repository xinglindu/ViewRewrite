import sqlparse

query = "SELECT column1, column2 FROM table1 WHERE column1 = 'value'"
parsed = sqlparse.parse(query)[0]
tokens = parsed.tokens
print(tokens)
print(sqlparse.sql.Statement(tokens).get_type())
print(sqlparse.sql.Comment(tokens))
inentifier = sqlparse.sql.Identifier(tokens)
print(inentifier.get_array_indices())
print([i for i in inentifier.get_array_indices()])
print(inentifier.get_ordering())
print(inentifier.get_typecast())
print(inentifier.is_wildcard())
print([i for i in sqlparse.sql.IdentifierList(tokens).get_identifiers()])
print([i for i in sqlparse.sql.IdentifierList(tokens)])  #
print(sqlparse.sql.Where(tokens))
print(sqlparse.sql.Case(tokens))
