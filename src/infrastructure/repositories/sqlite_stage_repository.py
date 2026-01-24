import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any

class StageStateRepository:
    """
    Repositório para persistência do estado da interface (Stage State).
    Salva coordenadas de páginas, zoom e visibilidade de painéis.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Inicializa o esquema do banco de dados SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            # Tabela para layout de páginas na Mesa de Luz
            conn.execute("""
                CREATE TABLE IF NOT EXISTS page_layouts (
                    doc_id TEXT,
                    page_index INTEGER,
                    x REAL,
                    y REAL,
                    rotation INTEGER,
                    PRIMARY KEY (doc_id, page_index)
                )
            """)
            # Tabela para preferências de UI
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ui_state (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

    def save_page_layout(self, doc_id: str, page_index: int, x: float, y: float, rotation: int):
        """Salva a posição e rotação de uma página específica."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO page_layouts (doc_id, page_index, x, y, rotation)
                VALUES (?, ?, ?, ?, ?)
            """, (doc_id, page_index, x, y, rotation))
            conn.commit()

    def get_page_layout(self, doc_id: str, page_index: int) -> Optional[Dict[str, Any]]:
        """Recupera o layout de uma página."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT x, y, rotation FROM page_layouts 
                WHERE doc_id = ? AND page_index = ?
            """, (doc_id, page_index))
            row = cursor.fetchone()
            if row:
                return {"x": row[0], "y": row[1], "rotation": row[2]}
        return None

    def save_ui_preference(self, key: str, value: Any):
        """Salva uma preferência de interface (ex: 'sidebar_left_visible', 'True')."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO ui_state (key, value)
                VALUES (?, ?)
            """, (key, str(value)))
            conn.commit()

    def get_ui_preference(self, key: str, default: Any = None) -> Any:
        """Recupera uma preferência de interface."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT value FROM ui_state WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default
