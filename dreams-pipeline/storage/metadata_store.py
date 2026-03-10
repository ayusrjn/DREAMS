import sqlite3
import os
from datetime import datetime
from typing import Optional
from models.memory import Memory
 
class MetadataStore:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to the data directory in the pipeline root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'data', 'dreams.db')
        
        self._conn = sqlite3.connect(db_path)
        self._create_tables()
 
    def _create_tables(self) -> None:
        self._conn.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                memory_id   TEXT PRIMARY KEY,
                user_id     TEXT NOT NULL,
                timestamp   TEXT NOT NULL,
                image_path  TEXT NOT NULL,
                caption     TEXT,
                scene_label TEXT,
                valence     REAL,
                arousal     REAL,
                dominance   REAL,
                gps_lat     REAL,
                gps_lon     REAL
            )
        ''')
        self._conn.commit()
 
    def save_memory(self, memory: Memory) -> None:
        vad = memory.vad or {}
        gps = memory.gps or (None, None)
        self._conn.execute(
            'INSERT OR REPLACE INTO memories VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            (memory.memory_id, memory.user_id, memory.timestamp.isoformat(),
             memory.image_path, memory.caption, memory.scene_label,
             vad.get('v'), vad.get('a'), vad.get('d'), # Updated to use v, a, d keys consistent with emotion extractor
             gps[0], gps[1])
        )
        self._conn.commit()
 
    def fetch_memories_by_user(self, user_id: str) -> list[Memory]:
        cursor = self._conn.execute(
            'SELECT * FROM memories WHERE user_id = ? ORDER BY timestamp ASC',
            (user_id,)
        )
        return [_row_to_memory(row) for row in cursor.fetchall()]
 
def _row_to_memory(row) -> Memory:
    return Memory(
        memory_id=row[0], user_id=row[1],
        timestamp=datetime.fromisoformat(row[2]),
        image_path=row[3], caption=row[4], scene_label=row[5],
        vad={'v': row[6], 'a': row[7], 'd': row[8]} if row[6] is not None else None, # Updated keys and added null check
        gps=(row[9], row[10]) if row[9] is not None else None
    )
