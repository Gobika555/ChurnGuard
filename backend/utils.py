import sqlite3

db = sqlite3.connect("data/churnguard.db")
cursor = db.cursor()

cursor.execute("""
SELECT user_id, COUNT(*)
FROM predictions
GROUP BY user_id
""")

print(cursor.fetchall())

db.close()