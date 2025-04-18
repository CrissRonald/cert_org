import sqlite3

conn = sqlite3.connect("certi_org.db")
cursor = conn.cursor()

cursor.execute("SELECT id, username, password FROM users")
rows = cursor.fetchall()

print("ID | Username | Password")
print("-" * 30)
for row in rows:
    print(row[0], "|", row[1], "|", row[2])

conn.close()
