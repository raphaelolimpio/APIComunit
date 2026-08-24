from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from jose import jwt, JWTError

from ..config import auth
from ..models import models
from ..api.db.database import get_db
from ..chat_manager import manager


router = APIRouter(tags=["Chat e Grupos"])

class GruposCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
class GruposResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    total_membros: int
    criado_em: datetime



@router.post("/grupos", response_model=GruposResponse, status_code=201)
def criar_grupo(
    payload: GruposCreate,
    usuario: models.Usuario = Depends(auth.obter_usuario_logado),
    db: Session = Depends(get_db)
):
    novo_grupo = models.Grupo(
        nome=payload.nome,
        descricao=payload.descricao,
        criador_id=usuario.id
    )
    novo_grupo.membros.append(usuario)
    db.add(novo_grupo)
    db.commit()
    db.refresh(novo_grupo)
    return GruposResponse(
        id=novo_grupo.id,
        nome=novo_grupo.nome,
        descricao=novo_grupo.descricao,
        total_membros=len(novo_grupo.membros),
        criado_em=novo_grupo.criado_em
    )

@router.post("/grupos/{grupo_id}/entrar")
def entrar_no_grupo(
    grupo_id: int,
    usuario: models.Usuario = Depends(auth.obter_usuario_logado),
    db: Session = Depends(get_db)
):
    grupo = db.query(models.Grupo).filter(models.Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado.")
    if usuario not in grupo.membros:
        grupo.membros.append(usuario)
        db.commit()
    return {"status": "Você entrou no grupo com sucesso."}

@router.get("/grupos/{grupo_id}/mensagens")
def historico_mensagens(
    grupo_id: int,
    limit: int = 50,
    usuario: models.Usuario = Depends(auth.obter_usuario_logado),
    db: Session = Depends(get_db)
):
    mensagens = (
        db.query(models.MensagemChat)
        .filter(models.MensagemChat.grupo_id == grupo_id)
        .order_by(models.MensagemChat.criado_em.asc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": m.id,
            "remetente_id": m.remetante_id,
            "remetente_nome": m.remetante.nome,
            "remetente_foto": m.remetante.foto_url,
            "conteudo": m.conteudo,
            "criado_em": m.criado_em.isoformat()
        }
        for m in mensagens
    ]

@router.websocket("/ws/chat/{grupo_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    grupo_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        usuario_id = int(payload.get("sub"))
        usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
        if not usuario:
            await websocket.close(code=4001)
            return
    except (JWTError, ValueError):
        await websocket.close(code=4001)
        return

    await manager.connect(grupo_id, websocket)
    try:
        while True:
            data= await websocket.receive_json()
            conteudo = data.get("conteudo", "").strip()

            if conteudo:
                nova_msg = models.MensagemChat(
                    grupo_id=grupo_id,
                    remetente_id=usuario.id,
                    conteudo=conteudo
                )
                db.add(nova_msg)
                db.commit()
                db.refresh(nova_msg)

                mensagem_payload = {
                    "id": nova_msg.id,
                    "grupo_id":grupo_id,
                    "remetente_id": usuario.id,
                    "remetente_nome": usuario.nome,
                    "rementente_foto": usuario.foto_url,
                    "conteudo": nova_msg.conteudo,
                    "criado_em": nova_msg.criado_em.isoformat()
                }
                await manager.broadcast_to_group(grupo_id, mensagem_payload)

    except WebSocketDisconnect:
        manager.disconnect(grupo_id, websocket)