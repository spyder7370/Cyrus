import sqlite3

conn = sqlite3.connect("cyrus.db")
conn.autocommit = True
cursor = conn.cursor()
