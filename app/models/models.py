from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Table
from sqlalchemy.orm import relationship
from ...api.db.database import Base

conversa_membros = Table(
    "conversa_membro",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("usuarios.id"),primary_key=True),
    Column("conversa_id", Integer, ForeignKey("conversas.id"), primary_key=True),
)

class Usuario(Base):
    __tablename__ = "usuarios"

    id =  Column(Integer, primary_key=True, index=True)
    google_id = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    nome = Column(String(100), nullable=False)
    foto_url = Column(String(300), nullable=True)
    bio= Column(String(250), nullable=True)
    fcm_token = Column(String(255), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    termos = relationship("Termo", back_populates="autor")
    explicacao = relationship("Explicacao", back_populates="autor")
    snippets = relationship("Snippet", back_populates="autor")
    comentarios = relationship("Comentaios", back_populates="autor")
    favoritos = relationship("Favoritos", back_populates="usuario")
    notificacao_recebidas = relationship("Notificacao", foreign_keys="Notificacao.destinatario_id", back_populates="destinatario")

class Comentario(Base):
    __tablename__ = "comentarios"

    id =  Column(Integer, primary_key=True, index=True)
    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo_alvo = Column(String(30), nullable=False)
    alvo_id = Column(Integer, nullable=False)
    parent_id = Column(Integer, ForeignKey("comentarios.id"),nullable=True)
    conteudo= Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    autor = relationship("Usuaario", back_populates="comentarios")
    resposta = relationship("Comentario", backref="comentario_pai", remote_side=[id])

class Favorito(Base):
    __tablename__ = "favoritos"

    id =  Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo_item = Column(String(30), nullable=False)
    item_id = Column(Integer, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="favoritos")

class Notificacao(Base):
    __tablename__ = "notificacoes"

    id =  Column(Integer, primary_key=True, index=True)
    destinatario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    remetente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo = Column(String(40), nullable=False)
    titulo = Column(String(100), nullable=False)
    mensagem = Column(String(255), nullable=False)
    rota= Column(String(150), nullable=True)
    lida = Column(Boolean, default= False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    destinatario = relationship("Usuario", foreign_keys=[destinatario_id], back_populates="notificacoes_recebidas")
    remetente = relationship("Usuario", foreign_keys=[remetente_id])

grupo_membros = Table(
    "grupo_membros",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("usuarios.id"), primary_key=True),
    Column("grupo_id",Integer, ForeignKey("grupos.id"), primary_key=True),
    Column("entrou_em", DateTime, default=datetime.utcnow)
)


class Grupo(Base):
    __tablename__ = "grupos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(255), nullable=True)
    criador_id = Column(Integer, ForeignKey("usuarios.id"),nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    membros = relationship("Usuario", secondary=grupo_membros, backref="meus_grupos")
    mensagens = relationship("MensagemChat", back_populates="grupo", cascade="all, delete-orphan")

class MensagemChat(Base):
    __tablename__ = "mensagens_chat"

    id = Column(Integer, primary_key=True, index=True)
    grupo_id = Column(Integer, ForeignKey("grupos.id"), nullable=False)
    remetante_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    conteudo = Column(Text, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
   

    conversa = relationship("Conversa", back_populates="mensagens")
    remetante = relationship("Usuario")

class Conversa(Base):
    __tablename__ = "conversas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=True)
    is_grupo = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    membros = relationship("Usuario", secondary=conversa_membros, backref="conversas")
    mensagem = relationship("MensagenChat", back_populates="conversa", cascade="all, delete-orphan")
