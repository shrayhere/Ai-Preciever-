import json
from .db import get_db_connection

class ScanRecord:
    @staticmethod
    def create(
        filename: str,
        ai_score: float,
        forensic_score: float,
        metadata_flags: list,
        final_score: float,
        category: str,
        explanation: str,
        heatmap_path: str = ""
    ) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        flags_str = json.dumps(metadata_flags) if isinstance(metadata_flags, (list, dict)) else str(metadata_flags)
        
        cursor.execute("""
            INSERT INTO scans (filename, ai_score, forensic_score, metadata_flags, final_score, category, explanation, heatmap_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (filename, ai_score, forensic_score, flags_str, final_score, category, explanation, heatmap_path))
        
        scan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return scan_id

    @staticmethod
    def get_by_id(scan_id: int) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            d = dict(row)
            try:
                d["metadata_flags"] = json.loads(d["metadata_flags"])
            except Exception:
                pass
            return d
        return None

    @staticmethod
    def get_recent(limit: int = 7) -> list:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scans ORDER BY upload_time DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        results = []
        for r in rows:
            d = dict(r)
            try:
                d["metadata_flags"] = json.loads(d["metadata_flags"])
            except Exception:
                pass
            results.append(d)
        return results

    @staticmethod
    def delete_all() -> list:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT filename, heatmap_path FROM scans")
        rows = cursor.fetchall()
        deleted_files = [dict(r) for r in rows]
        
        cursor.execute("DELETE FROM scans")
        conn.commit()
        conn.close()
        return deleted_files

