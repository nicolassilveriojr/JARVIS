import os
import sqlite3
import datetime
from core.security import JarvisSecurity

class JarvisMemory:
    def __init__(self, db_path=None):
        self.security = JarvisSecurity() # Inicializa criptografia
        if db_path is None:
            # Caminho padrão na nova estrutura
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_dir = os.path.join(base_dir, "data", "database")
            if not os.path.exists(db_dir): os.makedirs(db_dir)
            db_path = os.path.join(db_dir, "jarvis_memory.db")
            
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_input TEXT,
                jarvis_response TEXT,
                category TEXT DEFAULT 'conversation'
            )
        """)
        # Migração: Adiciona coluna 'category' se não existir
        try:
            self.cursor.execute("ALTER TABLE memory ADD COLUMN category TEXT DEFAULT 'conversation'")
        except sqlite3.OperationalError:
            pass

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                tags TEXT,
                timestamp TEXT
            )
        """)
        self.conn.commit()

    def save(self, user_input, response, category='conversation'):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if category != 'conversation':
            user_input = self.security.encrypt(user_input)
            response = self.security.encrypt(response)
            
        self.cursor.execute(
            "INSERT INTO memory (timestamp, user_input, jarvis_response, category) VALUES (?,?,?,?)",
            (ts, user_input, response, category)
        )
        self.conn.commit()

    def learn(self, key, value, tags=""):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        enc_value = self.security.encrypt(value)
        self.cursor.execute(
            "INSERT OR REPLACE INTO knowledge (key, value, tags, timestamp) VALUES (?,?,?,?)",
            (key, enc_value, tags, ts)
        )
        self.conn.commit()

    def recall(self, query):
        self.cursor.execute(
            "SELECT key, value FROM knowledge WHERE key LIKE ? OR tags LIKE ? OR value LIKE ?",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
        mems = self.cursor.fetchall()
        return [(k, self.security.decrypt(v)) for k, v in mems]

    def get_recent(self, limit=10, category='conversation'):
        self.cursor.execute(
            "SELECT timestamp, user_input, jarvis_response FROM memory WHERE category = ? ORDER BY id DESC LIMIT ?",
            (category, limit)
        )
        return self.cursor.fetchall()

    def clear_conversation(self):
        self.cursor.execute("DELETE FROM memory WHERE category = 'conversation'")
        self.conn.commit()
