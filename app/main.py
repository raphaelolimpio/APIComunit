from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.db.database import engine
from .models import models as user_models
from .api.models import modelsTerm as term_models

# Roteadores
from .config import auth
from .routers import chat, chatGrupo, comments, call
from .api import main as term_api

# Criação de todas as tabelas
user_models.Base.metadata.create_all(bind=engine)
term_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Comunit API - Rede Dev",
    description="Backend para termos técnicos, comunidade, chats e calls.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexão de todas as rotas
app.include_router(auth.router)                                    # /auth/google, /usuarios/me
app.include_router(term_api.router, prefix="/termos", tags=["Termos"]) # /termos/...
app.include_router(comments.router)                                # /comentarios/...
app.include_router(chat.router)                                    # /conversas/...
app.include_router(chatGrupo.router)                               # /grupos/...
app.include_router(call.router)                                    # /calls/...

@app.get("/", tags=["Healthcheck"])
def health_check():
    return {"status": "online", "service": "Comunit API"}