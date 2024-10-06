import sqlparse

sql = ""
parsed = sqlparse.parse(sql)[0]

print(parsed.tokens)
