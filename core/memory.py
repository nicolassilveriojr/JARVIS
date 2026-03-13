import sqlite3
import datetime


class JarvisMemory:
    def __init__(self, db_path="jarvis_memory.db"):
        self.conn   = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_input TEXT,
                jarvis_response TEXT
            )
        """)
        self.conn.commit()

    def save(self, user_input, response):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO memory (timestamp, user_input, jarvis_response) VALUES (?,?,?)",
            (ts, user_input, response)
        )
        self.conn.commit()

    def get_recent(self, limit=10):
        self.cursor.execute(
            "SELECT timestamp, user_input, jarvis_response FROM memory ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return self.cursor.fetchall()
