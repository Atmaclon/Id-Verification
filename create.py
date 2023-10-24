import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create a table to store user information
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    roll TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    branch TEXT NOT NULL,
    face_data BLOB
)
""")
conn.commit()
conn.close()