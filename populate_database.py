import csv
import sqlite3

conn = sqlite3.connect('natpark.db')
cur = conn.cursor()
cur.execute("""DROP TABLE IF EXISTS natpark""")
cur.execute("""CREATE TABLE natpark (name text, state text, year integer, area float)""")

with open('nationalparks.csv', 'r') as f:
    reader = csv.reader(f.readlines()[1:])
    cur.executemany("""INSERT INTO natpark VALUES (?,?,?,?)""", (row for row in reader))

conn.commit()
conn.close()
