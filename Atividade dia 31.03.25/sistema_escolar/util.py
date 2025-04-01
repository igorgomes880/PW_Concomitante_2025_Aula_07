from contextlib import contextmanager
import sqlite3

DB_NAME = 'dados_escola.db'

@contextmanager
def get_db_connection(db_name=DB_NAME):
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        yield conn
    except sqlite3.Error as e:
        print(f"Erro de conexão com o banco de dados: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.commit()
            conn.close()
