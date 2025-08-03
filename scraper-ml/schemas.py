from pydantic import BaseModel
from typing import Optional

class ProdutoSchema(BaseModel):
    nome: str
    preco: float
    link: str
    avaliacao: Optional[float]
    num_avaliacao: int

    class Config:
        orm_mode = True

class BuscaSchema(BaseModel):
    termo: str

    class Config:
        orm_mode = True
