import sqlite3
import pandas as pd

class SQLiteDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

    def init_schema(self) -> None:
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS estados (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, sigla TEXT NOT NULL UNIQUE)"
        )
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS cidades (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, estado_id INTEGER NOT NULL, FOREIGN KEY(estado_id) REFERENCES estados(id) ON DELETE CASCADE)"
        )
        self.conn.commit()

    def add_estado(self, nome: str, sigla: str) -> bool:
        try:
            self.conn.execute("INSERT INTO estados (nome, sigla) VALUES (?,?)", (nome.strip(), sigla.strip().upper()))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def add_cidade(self, nome: str, sigla_estado: str) -> bool:
        cur = self.conn.execute("SELECT id FROM estados WHERE sigla = ?", (sigla_estado.strip().upper(),))
        row = cur.fetchone()
        if not row:
            return False
        try:
            self.conn.execute("INSERT INTO cidades (nome, estado_id) VALUES (?,?)", (nome.strip(), row["id"]))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def list_estados(self) -> pd.DataFrame:
        return pd.read_sql_query("SELECT id, nome, sigla FROM estados ORDER BY sigla", self.conn)

    def list_cidades(self) -> pd.DataFrame:
        sql = "SELECT c.id, c.nome AS cidade, e.sigla AS estado FROM cidades c JOIN estados e ON e.id = c.estado_id ORDER BY e.sigla, c.nome"
        return pd.read_sql_query(sql, self.conn)

    def cidades_por_estado(self, sigla: str) -> pd.DataFrame:
        sql = "SELECT c.id, c.nome AS cidade FROM cidades c JOIN estados e ON e.id = c.estado_id WHERE e.sigla = ? ORDER BY c.nome"
        return pd.read_sql_query(sql, self.conn, params=(sigla.strip().upper(),))

    def all_cidades_nome(self) -> list:
        cur = self.conn.execute("SELECT c.nome, e.sigla FROM cidades c JOIN estados e ON e.id = c.estado_id ORDER BY e.sigla, c.nome")
        return [f"{r['nome']} - {r['sigla']}" for r in cur.fetchall()]

    def close(self) -> None:
        self.conn.close()
