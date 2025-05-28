import sqlite3
import os

# Configurable database path; defaults to /data/list.db for persistent disk
DATABASE_PATH = os.getenv("DATABASE_PATH", "/data/list.db")

class XenyList:
    def __init__(self):
        self.db_path = DATABASE_PATH

    def connect(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def initiate(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS anime (
                    title TEXT,
                    media_id INTEGER UNIQUE,
                    status TEXT,
                    score INTEGER,
                    progress INTEGER,
                    total INTEGER,
                    image TEXT,
                    notes TEXT,
                    isAdult BOOLEAN
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS manga (
                    title TEXT,
                    media_id INTEGER UNIQUE,
                    status TEXT,
                    score INTEGER,
                    progress INTEGER,
                    total INTEGER,
                    image TEXT,
                    notes TEXT,
                    isAdult BOOLEAN
                )
            """)
            conn.commit()
            print("Database initialized successfully.")

    def get_anime_list(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            query = cursor.execute("SELECT * FROM anime")
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in query.fetchall()]

    def get_manga_list(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            query = cursor.execute("SELECT * FROM manga")
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in query.fetchall()]

    def update_anime(self, media_id, progress, score, status):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE anime SET progress = ?, score = ?, status = ? WHERE media_id = ?
            """, (progress, score, status, media_id))
            conn.commit()

    def update_manga(self, media_id, progress, score, status):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE manga SET progress = ?, score = ?, status = ? WHERE media_id = ?
            """, (progress, score, status, media_id))
            conn.commit()

    def delete_anime(self, media_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM anime WHERE media_id = ?", (media_id,))
            conn.commit()

    def delete_manga(self, media_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM manga WHERE media_id = ?", (media_id,))
            conn.commit()

    def check_anime_exists(self, media_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM anime WHERE media_id = ?", (media_id,))
            return cursor.fetchone() is not None

    def check_manga_exists(self, media_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM manga WHERE media_id = ?", (media_id,))
            return cursor.fetchone() is not None

    def add_media(self, media_type, title, media_id, status, score, progress, total, image, notes, isAdult):
        with self.connect() as conn:
            cursor = conn.cursor()
            if media_type not in ["anime", "manga"]:
                raise ValueError("Invalid media_type")
            cursor.execute(f"""
                INSERT OR IGNORE INTO {media_type} (title, media_id, status, score, progress, total, image, notes, isAdult)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, media_id, status, score, progress, total, image, notes, isAdult))
            conn.commit()

# Singleton instance
xenylist = XenyList()
