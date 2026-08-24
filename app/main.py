from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from .models import models
from .config import auth
from .api.db.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dev Comunity API")

class GoogleAuthRequest(BaseModel):
    id_token: str

class FCMTokenRequest(BaseModel):
    fcm_token: int

@app.post("/auth/google")
def login_google(payload: GoogleAuthRequest, db: Session = Depends(get_db)):
    google_data = auth.verificar_google_token(payload.id_token)

    google_id = google_data["sub"]
    email = google_data["email"]
    nome = google_data.get("name", "Dev Anônimo")
    foto = google_data.get("picture", "")

    usuario = db.query(models.Usuario).filter(models.Usuario.google_id == google_id).first()
    if not usuario:
        usuario = models.Usuario(
            google_id=google_id,
            email=email,
            nome=nome,
            foto_url=foto
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

    token_jwt = auth.criar_acess_token({"sub": str(usuario.id)})

    return {
        "acess_token": token_jwt,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "foto_url": usuario.foto_url
        }
    }

@app.get("/usuarios/me")
def meu_perfil(usuario: models.Usuario = Depends(auth.obter_usuario_logado)):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "foto_url": usuario.foto_url,
        "bio": usuario.bio,
        "total_termos": len(usuario.termos),
        "total_explicacoes": len(usuario.explicacoes),
        "total_snippets": len(usuario.snippets),

    }

@app.post("/usuarios/me/fcm-token")
def atualizar_fcm_token(
    payload: FCMTokenRequest,
    usuario: models.Usuario = Depends(auth.obter_usuario_logado),
    db: Session = Depends(get_db)
):
    usuario.fcm_token = payload.fcm_token
    db.commit()
    return {"status": "token atualizado"}