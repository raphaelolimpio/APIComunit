from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from . import schemas
from .db.database import engine, get_db
from .models import modelsTerm

modelsTerm.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dev Community Dictionary API",
    description="API colaborativa para termos tecnicos e snippets de codigo"
) 

@app.post("/termos/", response_model=schemas.TermosResponse, status_code=201)
def criar_termo(termo: schemas.TermosCreate, db: Session = Depends(get_db)):
    db_termo = db.query(modelsTerm.Termo).filter(modelsTerm.Termo.titulo.ilike(termo.titulo)).first()
    if db_termo:
        return HTTPException(status_code=400, detail="Este termo ja esta cadastrado")
    novo_termo = modelsTerm.Termo(**termo.model_dump())
    db.add(novo_termo)
    db.commit()
    db.refresh(novo_termo)
    return novo_termo

@app.get("/termos/", response_model=List[schemas.TermosResponse])
def listar_termos(
    busca: Optional[str] = Query(None, description="Filtrar por nome ou catrgoria"),
    db: Session = Depends(get_db)
):
    query = db.query(modelsTerm.Termo)
    if busca:
        query = query.filter(
            (modelsTerm.Termo.titulo.ilike(f"%{busca}%")) |
            (modelsTerm.Termo.categoria.ilike(f"%{busca}%"))
        )
    return query.all()

@app.get("/termos/{termos_id}", response_model=schemas.TermosResponse)
def obter_termo(termo_id: int, db: Session = Depends(get_db)):
    db_termo = db.query(modelsTerm.Termo).filter(modelsTerm.Termo.id == termo_id).first()
    if not db_termo:
        raise HTTPException(status_code=404, detail="Termo não encontrado")
    return db_termo

@app.post("termos/{termo_id}/explicacoes", response_model=schemas.ExplicacaoResponse, status_code=201)
def adicionar_explicacao(termo_id: int, exp: schemas.ExplicacaoCreate, db: Session = Depends(get_db)):
    db_termo = db.query(modelsTerm.Termo).filter(modelsTerm.Termo.id == termo_id).first()
    if not db_termo:
        raise HTTPException(status_code=404, detail="Termo não encontrado")
    nova_exp = modelsTerm.Explicacao(**exp.model_dump(), termo_id=termo_id)
    db.add(nova_exp)
    db.commit()
    db.refresh(nova_exp)
    return nova_exp

@app.post("/explicacoes/{explicacoes_id}/like", response_model=schemas.ExplicacaoResponse)
def dar_like_explicacao(explicacao_id: int, db: Session = Depends(get_db)):
    exp = db.query(modelsTerm.Explicacao).filter(modelsTerm.Explicacao.id == explicacao_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Explicação não encontrado")
    exp.upvotes += 1
    db.commit()
    db.refresh(exp)
    return exp

@app.post("/snippets/", response_model=schemas.SnipperResponse, status_code=201)
def criar_snipepet(snippet: schemas.SnipperResponse, db: Session = Depends(get_db)):
    if snippet.termo_id:
        db_termo = db.query(modelsTerm.Termo).filter(modelsTerm.Termo.id == snippet.termo_id).first()
        if not db_termo:
            raise HTTPException(status_code=404, detail="TErmo vinculado não encontrado")
        novo_snippet = modelsTerm.Snippet(**snippet.model_dump())
        db.add(novo_snippet)
        db.commit()
        db.refresh(novo_snippet)
        return novo_snippet

@app.get("/snippets/", response_model=List[schemas.SnipperResponse])
def listar_snippets(linguagem: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(modelsTerm.Snippet)
    if linguagem:
        query = query.filter(modelsTerm.Snippet.linguagem.ilike(linguagem))
    return query.order_by(modelsTerm.Snippet.upvotes.desc()).all()

@app.post("/snippets/{snippet_id}/like", response_model=schemas.SnipperResponse)
def dar_like_snippet(snippet_id: int, db: Session = Depends(get_db)):
    snip = db.query(modelsTerm.Snippet).filter(modelsTerm.Snippet.id == snippet_id).first()
    if not snip:
        raise HTTPException(status_code=404, detail="Snippet não encontrado")
    snip.upvotes += 1
    db.commit()
    db.refresh(snip)
    return snip