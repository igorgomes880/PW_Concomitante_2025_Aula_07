CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    matricula TEXT NOT NULL UNIQUE,
    curso TEXT NOT NULL,
    notas TEXT NOT NULL
)
"""

INSERT_ALUNO = """
INSERT INTO alunos (nome, matricula, curso, notas)
VALUES (?, ?, ?, ?)
"""

SELECT_ALUNO = """
SELECT id, nome, matricula, curso, notas
FROM alunos
WHERE id = ?
"""

SELECT_TODOS_ALUNOS = """
SELECT id, nome, matricula, curso, notas
FROM alunos
"""

UPDATE_ALUNO = """
UPDATE alunos
SET nome = ?, matricula = ?, curso = ?, notas = ?
WHERE id = ?
"""

DELETE_ALUNO = """
DELETE FROM alunos
WHERE id = ?
"""
