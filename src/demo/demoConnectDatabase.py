import psycopg2

conn = psycopg2.connect(database="tpc-h-10", user="postgres", password="root", host="localhost", port="5432")

cur = conn.cursor()

cur.execute("")

rows = cur.fetchall()

for row in rows:
    print(row)

cur.close()
conn.close()
