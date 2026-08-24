from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models import models
from ..config import auth
from ...api.db.database import get_db

router = APIRouter(tags=["Conversa"])

@router.post("/conversas/direta/{destinatario_id}")
def iniciar_chat_direto(
    destinatario_id: int,
    usuario: models.Usuario = Depends(auth.obter_usuario_logado),
    db: Session = Depends(get_db)
):
    if usuario.id == destinatario_id:
        raise HTTPException(status_code=400, detail= "Voce não pode criar um chat com voce mesmo.")
    destinatario = db.query(models.Usuario).filter(models.Usuario.id == destinatario_id).first()
    if not destinatario:
        raise HTTPException(status_code=404, detail="Usuario destiantario não encontrado")

    conversa_existente = (
        db.query(models.Conversa)
        .filter(models.Conversa.is_grupo == False)
        .filter(models.Conversa.membros.contains(usuario))
        .filter(models.Conversa.membros.contains(destinatario))
        .first()
    )

    if conversa_existente:
        return {"conversa_id": conversa_existente.id, "novo": False}

    nova_conversa = models.Conversa(is_grupo=False)
    nova_conversa.membros.extend([usuario, destinatario])
    db.add(nova_conversa)
    db.commit()
    db.refresh(nova_conversa)

    return {"conversa_id": nova_conversa.id, "novo": True}