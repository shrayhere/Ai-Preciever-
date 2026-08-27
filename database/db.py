import sqlite3
import os
import shutil
import tempfile

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOCAL_DB_PATH = os.path.join(BASE_DIR, "deepverify.db")

def get_db_path():
    try:
        test_path = os.path.join(BASE_DIR, ".db_write_test")
        with open(test_path, "w") as f:
            f.write("test")
        os.remove(test_path)
        return LOCAL_DB_PATH
    except Exception:
        tmp_db_path = os.path.join(tempfile.gettempdir(), "deepverify.db")
        if not os.path.exists(tmp_db_path) and os.path.exists(LOCAL_DB_PATH):
            try:
                shutil.copy2(LOCAL_DB_PATH, tmp_db_path)
            except Exception:
                pass
        return tmp_db_path

def get_db_connection():
    db_file = get_db_path()
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates SQLite scans table if it does not exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            ai_score REAL,
            forensic_score REAL,
            metadata_flags TEXT,
            final_score REAL,
            category TEXT,
            explanation TEXT,
            heatmap_path TEXT
        );
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database init warning: {e}")

