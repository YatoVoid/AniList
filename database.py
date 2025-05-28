import sqlite3
import os

# Define a fallback local path
DEFAULT_DB_PATH = 'list.db'
# Use environment variable DATABASE_PATH or default to /data/list.db (for Render)
DATABASE_PATH = os.getenv('DATABASE_PATH', '/data/list.db')

# Ensure the directory exists
db_dir = os.path.dirname(DATABASE_PATH)
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir)
    print(f"Created database directory: {db_dir}")

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
            print(f"Database initialized successfully at {self.db_path}")

    def get_list(self, media_type):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {media_type}")
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_anime_list(self):
        return self.get_list("anime")

    def get_manga_list(self):
        return self.get_list("manga")

    def update_media(self, media_type, media_id, progress, score, status):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE {media_type} SET progress = ?, score = ?, status = ? WHERE media_id = ?
            """, (progress, score, status, media_id))
            conn.commit()

    def update_anime(self, media_id, progress, score, status):
        self.update_media("anime", media_id, progress, score, status)

    def update_manga(self, media_id, progress, score, status):
        self.update_media("manga", media_id, progress, score, status)

    def delete_media(self, media_type, media_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {media_type} WHERE media_id = ?", (media_id,))
            conn.commit()

    def delete_anime(self, media_id):
        self.delete_media("anime", media_id)

    def delete_manga(self, media_id):
        self.delete_media("manga", media_id)

    def check_media_exists(self, media_type, media_id):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT 1 FROM {media_type} WHERE media_id = ?", (media_id,))
            return cursor.fetchone() is not None

    def check_anime_exists(self, media_id):
        return self.check_media_exists("anime", media_id)

    def check_manga_exists(self, media_id):
        return self.check_media_exists("manga", media_id)

    def add_media(self, media_type, title, media_id, status, score, progress, total, image, notes, isAdult):
        if media_type not in ["anime", "manga"]:
            raise ValueError("Invalid media_type")
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT OR IGNORE INTO {media_type} (title, media_id, status, score, progress, total, image, notes, isAdult)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, media_id, status, score, progress, total, image, notes, isAdult))
            conn.commit()

# Singleton instance
xenylist = XenyList()
