import sqlite3

conn = sqlite3.connect("test.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        completed INTEGER NOT NULL
    )
    """
)
conn.commit()
