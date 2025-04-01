import sqlite3
from typing import List, Optional
from alunos.aluno import Aluno
from alunos import aluno_sql as sql
from util import get_db_connection

class AlunoRepo:
    def __init__(self):
        self._criar_tabela()

    def _criar_tabela(self):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql.CREATE_TABLE)
        except sqlite3.Error as e:
            print(f"Erro ao criar tabela: {e}")

    def adicionar(self, aluno: Aluno) -> Optional[int]:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                notas_str = ",".join(map(str, aluno.notas))
                cursor.execute(sql.INSERT_ALUNO, (aluno.nome, aluno.matricula, aluno.curso, notas_str))
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar aluno: {e}")
            return None

    def obter(self, aluno_id: int) -> Optional[Aluno]:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql.SELECT_ALUNO, (aluno_id,))
                row = cursor.fetchone()
                if row:
                    notas = list(map(float, row[4].split(',')))
                    return Aluno(id=row[0], nome=row[1], matricula=row[2], curso=row[3], notas=notas)
                return None
        except sqlite3.Error as e:
            print(f"Erro ao obter aluno {aluno_id}: {e}")
            return None

    def obter_todos(self) -> List[Aluno]:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql.SELECT_TODOS_ALUNOS)
                rows = cursor.fetchall()
                return [Aluno(id=row[0], nome=row[1], matricula=row[2], curso=row[3], notas=list(map(float, row[4].split(',')))) for row in rows]
        except sqlite3.Error as e:
            print(f"Erro ao obter todos os alunos: {e}")
            return []

    def atualizar(self, aluno: Aluno) -> bool:
        if aluno.id is None:
            print("Erro: Aluno sem ID não pode ser atualizado.")
            return False
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                notas_str = ",".join(map(str, aluno.notas))
                cursor.execute(sql.UPDATE_ALUNO, (aluno.nome, aluno.matricula, aluno.curso, notas_str, aluno.id))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao atualizar aluno {aluno.id}: {e}")
            return False

    def excluir(self, aluno_id: int) -> bool:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql.DELETE_ALUNO, (aluno_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao excluir aluno {aluno_id}: {e}")
            return False
