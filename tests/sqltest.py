import sqlite3
import os

conn = sqlite3.connect('user.db')
c = conn.cursor()

users = c.execute('''SELECT * FROM users''')
for row in c:
    print(row)

print(users)