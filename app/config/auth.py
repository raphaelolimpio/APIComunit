from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.orm import Session

from ..models import models
from ..api.db.database import get_db


SECRET_KEY = "SUA_CHAVE_SUPER_SECRETA_MUDE_EM_PROD"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
GOOGLE_CLIENT_ID = "SEU_GOOGLE_CLIENT_ID_DO_CONSOLE"

security = HTTPBearer()

def criar_acess_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verificar_google_token(token: str):
    try:
        id_info = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
        return id_info
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token do google inválido ou expirado."
        )

def obter_usuario_logado(
        cred: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> models.Usuario:
    token = cred.credentials
    try:
        payload = jwt. decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: int = payload.get("sub")
        if usuario_id is None:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token JWT inválido")

    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")
    return usuario