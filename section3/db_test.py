import sqlite3


connection = sqlite3.connect('../../data.db')

cursor = connection.cursor()

try:
    create_table = "CREATE TABLE users (id int, username text, password text)"
    cursor.execute(create_table)
except sqlite3.OperationalError:
    print('table users already exists, skipping creation')


user = (1, 'alex', 'asdf')
insert_query = "INSERT INTO users VALUES (?, ?, ?)"
cursor.execute(insert_query, user)


users = [
    (2, 'rolf', 'asdf'),
    (3, 'aaaa', 'asdf')
]

cursor.executemany(insert_query, users)


select_query = "SELECT * FROM users"
for row in cursor.execute(select_query):
    print(row)

connection.commit()
connection.close()
