from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ExplicacaoCreate(BaseModel):
    autor: Optional[str] = "Anônimo"
    conteudo: str
    nivel: Optional[str] = "Geral"

class ExplicacaoResponse(ExplicacaoCreate):
    id: int
    termo_id: int
    criado_em: datetime

    class Config:
        from_attributes = True

class SnipperCreate(BaseModel):
    termo_id: Optional[int] = None
    autor: Optional[str] = "Anônimo"
    titulo: str
    linguagem: str
    codigo: str
    explicaçao: str

class SnipperResponse(SnipperCreate):
    id: int
    upvotes: int
    criado_em: datetime

    class Config:
        from_attributes = True

class TermosCreate(BaseModel):
    titulo: str
    categoria: Optional[str] = "Geral"

class TermosResponse(TermosCreate):
    id: int
    criado_em: datetime
    explicacoes: List[ExplicacaoResponse] = []
    snippets: List[SnipperResponse] = []

    class Config:
        from_attributes = True