import sqlite3


class DBManager:
    """Gestiona la conexión y operaciones sobre la base de datos SQLite."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn    = sqlite3.connect(self.db_path)
        self.cursor  = self.conn.cursor()

    # ------------------------------------------------------------------
    def create_table(self):
        """Crea la tabla principal si no existe, con columna confianza_ia."""
        query = """
        CREATE TABLE IF NOT EXISTS observaciones_catastro (
            id_predio    TEXT PRIMARY KEY,
            fecha        TEXT,
            sector       TEXT,
            observacion  TEXT,
            categoria_ia TEXT,
            confianza_ia REAL
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    # ------------------------------------------------------------------
    def insert_data(self, data_list: list[dict]):
        """Inserta registros desde una lista de dicts (ignora duplicados)."""
        query = """
        INSERT OR IGNORE INTO observaciones_catastro
            (id_predio, fecha, sector, observacion)
        VALUES (?, ?, ?, ?)
        """
        records = [
            (d["id_predio"], d["fecha"], d["sector"], d["observacion"])
            for d in data_list
        ]
        self.cursor.executemany(query, records)
        self.conn.commit()
        print(f"Se insertaron/verificaron {len(records)} registros.")

    # ------------------------------------------------------------------
    def get_unclassified(self) -> list[tuple]:
        """Devuelve (id_predio, observacion) de registros sin clasificar."""
        query = """
        SELECT id_predio, observacion
        FROM observaciones_catastro
        WHERE categoria_ia IS NULL
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    # ------------------------------------------------------------------
    def update_classification(self, id_predio: str, categoria: str, confianza: float):
        """Actualiza categoría y confianza de un registro."""
        query = """
        UPDATE observaciones_catastro
        SET categoria_ia = ?, confianza_ia = ?
        WHERE id_predio = ?
        """
        self.cursor.execute(query, (categoria, confianza, id_predio))
        self.conn.commit()

    # ------------------------------------------------------------------
    def get_all_classified(self) -> list[tuple]:
        """Devuelve todos los registros ya clasificados."""
        query = """
        SELECT id_predio, fecha, sector, observacion, categoria_ia, confianza_ia
        FROM observaciones_catastro
        WHERE categoria_ia IS NOT NULL
        ORDER BY sector, id_predio
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    # ------------------------------------------------------------------
    def get_stats(self) -> list[tuple]:
        """Cuenta registros por categoría, ordenados de mayor a menor."""
        query = """
        SELECT categoria_ia, COUNT(*) AS total,
               ROUND(AVG(confianza_ia), 3) AS confianza_promedio
        FROM observaciones_catastro
        WHERE categoria_ia IS NOT NULL
        GROUP BY categoria_ia
        ORDER BY total DESC
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    # ------------------------------------------------------------------
    def get_low_confidence(self, threshold: float = 0.40) -> list[tuple]:
        """Devuelve registros cuya confianza esté por debajo del umbral."""
        query = """
        SELECT id_predio, observacion, categoria_ia, confianza_ia
        FROM observaciones_catastro
        WHERE confianza_ia < ? AND categoria_ia IS NOT NULL
        ORDER BY confianza_ia ASC
        """
        self.cursor.execute(query, (threshold,))
        return self.cursor.fetchall()

    # ------------------------------------------------------------------
    def delete_record(self, id_predio: str):
        """Elimina un registro por su ID (usado en correcciones)."""
        query = "DELETE FROM observaciones_catastro WHERE id_predio = ?"
        self.cursor.execute(query, (id_predio,))
        self.conn.commit()

    # ------------------------------------------------------------------
    def close(self):
        self.conn.close()
