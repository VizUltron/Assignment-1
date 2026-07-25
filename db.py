import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")

conn = psycopg.connect(db_url)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM tasks")
count = cursor.fetchone()[0]

if count == 0:
    cursor.executemany(
        "INSERT INTO tasks (title, done) VALUES (%s, %s)",
        [
            ("Learn FastAPI", False),
            ("Build CRUD API", False),
            ("Submit Assignment", False),
        ]
    )
    conn.commit()