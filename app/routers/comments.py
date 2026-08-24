from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ..models import models
from ..api.models import modelsTerm
from ..config import auth
from ..api.db.database import get_db

router = APIRouter(prefix="/comentarios", tags=["Comentarios"])

class ComentariosCreate(BaseModel):
    tipo_alvo: str
    alvo_id: int
    conteudo: str
    parent_id: Optional[int] = None

class ComentarioResponse(BaseModel):
    id: int
    autor_id: int
    autor_nome: str
    autor_foto: Optional[str]
    conteudo: str
    parent_id: Optional[int]
    criado_em: datetime
    respostas: List["ComentarioResponse"] = []

    class Config:
        from_attributes = True

@router.post("/", response_model=ComentarioResponse, status_code=201)
def criar_comentario(
    payload: ComentariosCreate,
    usuario: models.Usuario = Depends(auth.obter_usuario_logado),
    db: Session =  Depends(get_db)
):
    novo_comnetario = models.Comentario(
        autor_id=usuario.id,
        tipo_alvo=payload.tipo_alvo,
        alvo_id=payload.alvo_id,
        parent_id=payload.parent_id,
        conteudo=payload.conteudo
    )
    db.add(novo_comnetario)
    db.flush()

    destinatario_id = None
    titulo_notif = ""
    msg_notif = ""

    if payload.parent_id:
        comentario_pai = db.query(models.Comentario).filter(models.Comentario.id == payload.parent_id).first()
        if comentario_pai and comentario_pai.autor_id != usuario.id:
            destinatario_id = comentario_pai.autor_id
            titulo_notif = f"{usuario.nome} respondeu ao seu comentário"
            msg_notif = payload.conteudo[:100]
        else:
            if payload.tipo_alvo == "snippet":
                item = db.query(modelsTerm.Snippet).filter(modelsTerm.Snippet.id == payload.alvo_id).first()
                if item and item.autor.id != usuario.id:
                    destinatario_id = item.autor_id
                    titulo_notif = f"{usuario.nome} comentou no seu snippet"
                    msg_notif = payload.conteudo[:100]
                elif payload.tipo_alvo == "explicacao":
                    item = db.query(modelsTerm.Explicacao).filter(modelsTerm.Explicacao.id == payload.alvo_id).first()
                    if item and item.autor_id != usuario.id:
                        destinatario_id = item.autor_id
                        titulo_notif = f"{usuario.nome} comentou na sua explicação"
                        msg_notif = payload.conteudo[:100]

    if destinatario_id:
        notificacao = models.Notificacao(
            destinatario_id=destinatario_id,
            remetente_id=usuario.id,
            tipo="comentario" if not payload.parent_id else "resposta",
            titulo=titulo_notif,
            mensagem=msg_notif,
            rota=f"/{payload.tipo_alvo}/{payload.alvo_id}"

        )
        db.add(notificacao)
        db.commit()
        db.refresh(notificacao)

        return ComentarioResponse(
            id=novo_comnetario.id,
            autor_id=usuario.id,
            autor_nome=usuario.nome,
            autor_foto=usuario.foto_url,
            conteudo=novo_comnetario.conteudo,
            parent_id=novo_comnetario.parent_id,
            criado_em=novo_comnetario.criado_em,
            respostas=[]
        )

@router.get("/{tipo_alvo}/{alvo_id}", response_model=List[ComentarioResponse])
def listar_comentarios_arvore(tipo_alvo: str, alvo_id: int, db: Session = Depends(get_db)):
    comentarios = (
        db.query(models.Comentario).filter(
            models.Comentario.tipo_alvo == tipo_alvo,
            models.Comentario.alvo_id == alvo_id,
            models.Comentario.parent_id == None
        )
        .order_by(models.Comentario.criado_em.asc())
        .all()
    )
    def montar_arvore(c: models.Comentario) -> ComentarioResponse:
        return ComentarioResponse(
            id=c.id,
            autor_id=c.autor.id,
            autor_nome=c.autor.nome,
            autor_foto=c.autor.foto_url,
            conteudo=c.conteudo,
            parent_id=c.parent_id,
            criado_em=c.criado_em,
            respostas=[montar_arvore(filho) for filho in c.resposta]
        )
    return [montar_arvore(c) for c in comentarios]