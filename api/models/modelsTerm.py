from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Table
from sqlalchemy.orm import relationship
from ..db.database import Base

class Termo(Base):
    __tablename__ = "termos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), unique=True, index=True, nullable=False)
    categoria = Column(String(50), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    explicacoes = relationship("Explicacao", back_populates="termo", cascade="all, delete-orphan")
    snippets = relationship("Snippet", back_populates="termo", cascade="all, delete-orphan")    

class Snippet(Base):
    __tablename__ = "snippets"

    id = Column(Integer, primary_key=True, index=True)
    termo_id = Column(Integer, ForeignKey("termos.id"), nullable=True)
    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    titulo = Column(String(120), nullable=False)
    linguagem = Column(String(40), nullable=False)
    codigo = Column(Text, nullable=False)
    explicacao = Column(Text, nullable=False)
    upvotes = Column(Integer, default=0)
    criado_em = Column(DateTime, default=datetime.utcnow)

    termo = relationship("Termo", back_populates="snippets")
    autor = relationship("Usuario", back_populates="snippets")
    
class Explicacao(Base):
    __tablename__ = "explicacoes"

    id = Column(Integer, primary_key=True, index=True)
    termo_id = Column(Integer, ForeignKey("termos.id"), nullable=False)
    autor = Column(String(80), default="Anônimo", nullable=False)
    titulo = Column(String(120), nullable=False)
    linguagem = Column(String(50), nullable=False)
    codigo = Column(Text, nullable=False)
    explicacao = Column(Text, nullable=False)
    upvotes = Column(Integer, default=0)
    criado_em = Column(DateTime, default=datetime.utcnow)

    termo = relationship("Termo", back_populates="explicacoes")

