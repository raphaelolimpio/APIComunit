from fastapi import APIRouter, Depends, HTTPException
from livekit import api
from sqlalchemy.orm import Session

from ..models import models
from ..config import auth
from ..api.db.database import get_db

router = APIRouter(prefix="/calls", tags=["Video chamada"])

LIVEKIT_API_KEY = ""
LIVEKIT_API_SECRET = ""

@router.post("/token/{conversa_id}")
def gerar_token_call(
    conversa_id: int,
    usuario: models.Usuario = Depends(auth.obter_usuario_logado),
    db: Session = Depends(get_db)
):
    conversa = db.query(models.Conversa).filter(models.Conversa.id == conversa_id).first()
    if not conversa or usuario not in conversa.membros:
        raise HTTPException(status_code=403, detail="Acesso não autorixado a esta chamada")

    nome_sala = f"room_conversa_{conversa_id}"

    token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
        .with_identity(str(usuario.id)) \
        .with_name(usuario.nome) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=nome_sala,
            can_publish=True,
            can_subscribe=True
        ))
    return {
        "room_name": nome_sala,
        "tokne": token.to_jwt(),
        "livekit_url": "wss://"
    }