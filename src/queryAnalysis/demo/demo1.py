import sqlparse
from collections import deque

sql = "SELECT customers.customer_id, customers.customer_name, orders.order_date FROM customers INNER JOIN orders ON customers.customer_id = orders.customer_id WHERE customers.city = 'New York' ORDER BY orders.order_date DESC LIMIT 10"

parsed = sqlparse.parse(sql)[0]


def bfs_parse_tree(tree):
    queue = deque([tree])
    while queue:
        node = queue.popleft()
        print(node.ttype, node.value)
        for child in node.tokens:
            if isinstance(child, sqlparse.sql.TokenList):
                queue.append(child)
            elif isinstance(child, sqlparse.sql.Token):
                queue.append(sqlparse.sql.TokenList([child]))
            # Ignore anything else


bfs_parse_tree(parsed)
