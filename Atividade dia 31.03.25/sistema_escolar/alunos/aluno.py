from pydantic import BaseModel, validator, Field
from typing import List, Optional

class Aluno(BaseModel):
    id: Optional[int] = None
    nome: str = Field(..., min_length=3, max_length=100)
    matricula: str = Field(..., max_length=7)
    curso: str = Field(..., min_length=3, max_length=50)
    notas: List[float] = Field(..., min_items=1, max_items=4)

    @validator('notas')
    def validar_notas(cls, notas):
        if any(nota < 0 or nota > 10 for nota in notas):
            raise ValueError("As notas devem estar entre 0 e 10.")
        return notas
