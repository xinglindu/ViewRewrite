import re
import psycopg2
import sys

from lexerAnalysis import lexerCheck


def checkSqlError(sql):
    conn = psycopg2.connect(database="tpc-h-10", user="postgres", password="root", host="localhost", port="5432")
    cur = conn.cursor()
    try:
        cur.execute(sql)
    except psycopg2.Error as e:
        return "There is an error in the sql statement\n" + str(e)
    cur.close()
    conn.close()
    return sql


def getAllTableList():
    conn = psycopg2.connect(database="tpc-h-10", user="postgres", password="root", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'")
    rows = cur.fetchall()
    tableAllList = []
    for row in rows:
        tableAllList.append(row[0])
    cur.close()
    conn.close()
    return tableAllList


def extract_table_names(query):
    table_names = re.findall(r'(?:FROM|JOIN|,)\s+(\w+)', query, flags=re.IGNORECASE)
    subqueries = re.findall(r'\(([^()]+)\)', query)
    subquery_tables = []
    for subquery in subqueries:
        subquery_tables += extract_table_names(subquery)
    allTableList = getAllTableList()
    relateTable = list(table_names + subquery_tables)
    resultTable = []
    for i in relateTable:
        if i in allTableList:
            resultTable.append(i)
    return resultTable


def getTableFilterProperties(query):
    match = re.search(r'\bWHERE\b(.*)', query, re.IGNORECASE)
    if match:
        where_clause = match.group(1).strip()
        # print("", where_clause)
        conditions = re.findall(
            r'\b(\w+)\b\s*(=|>|<|>=|<=|<>|LIKE|NOT\s+LIKE|BETWEEN\s+AND|IN|NOT\s+IN|IS\s+(?:NOT\s+)?NULL)\s*((?:(?:(?<!\\)[\'"]).*?(?<!\\)(?:[\'"]))|(?:\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)(?:\s*,\s*(?:\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?))*)',
            where_clause, re.IGNORECASE)
        properties = [condition[0] for condition in conditions]
        return properties
    else:
        return []


def getPrimaryKey(tableName):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database="tpc-h-10", user="postgres", password="root", host="localhost", port="5432")

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Define the table name as a variable
    table_name = tableName

    # Execute the SQL query to get the primary key of a table with a parameterized query
    query = """
        SELECT
            pg_attribute.attname,
            format_type(pg_attribute.atttypid, pg_attribute.atttypmod) AS data_type
        FROM pg_index, pg_class, pg_attribute
        WHERE
            pg_class.oid = %s::regclass AND
            indrelid = pg_class.oid AND
            pg_attribute.attrelid = pg_class.oid AND
            pg_attribute.attnum = any(pg_index.indkey)
            AND indisprimary;
    """
    cur.execute(query, (table_name,))

    # Fetch the results and print them
    rows = cur.fetchall()
    primaryKeyName = []
    for row in rows:
        primaryKeyName.append(row[0])
    # Close the cursor and database connection
    cur.close()
    conn.close()
    return primaryKeyName


def getDependencies(table):
    conn = psycopg2.connect(database="tpc-h-10", user="postgres", password="root", host="localhost", port="5432")
    cur = conn.cursor()
    table_name = table
    cur.execute("""
        SELECT
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
        WHERE 
            constraint_type = 'FOREIGN KEY' AND tc.table_name=%s;
    """, (table_name,))
    rows = cur.fetchall()
    foreignTableList = []
    for row in rows:
        # print("Table name:", row[0])
        # print("Column name:", row[1])
        # print("Foreign table name:", row[2])
        # print("Foreign column name:", row[3])
        foreignTableList.append(row[2])
    cur.close()
    conn.close()
    return set(foreignTableList)


if __name__ == "__main__":
    checkSqlError("1")
    sql_query = ""
    lexerResult = lexerCheck(sql_query)
    table_names = extract_table_names(lexerResult)
    print(table_names)
    properties = getTableFilterProperties("SELECT COUNT(*) FROM sc WHERe sno=1 AND cno=1")
    print(properties)
