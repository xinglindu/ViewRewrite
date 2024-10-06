import sqlparser

query = "SELECT a, b FROM table_1 WHERE c > 20"
# Init a oracle sql parser
parser = sqlparser.Parser()
print(parser.check_syntax(query))
# Check for syntax errors
if parser.check_syntax(query) == 0:
    # Get first statement from the query
    stmt = parser.get_statement(0)

    # Get root node
    root = stmt.get_root()

    print(root.__dict__)
