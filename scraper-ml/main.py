from fastapi import FastAPI, Query, Depends
from typing import List
from database import Base, engine, SessionLocal, Produto, Busca
from scraper import buscar_produtos
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from schemas import ProdutoSchema, BuscaSchema
import uvicorn

app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"mensagem": "API de busca Mercado Livre. Use /buscar-produtos?termo=produto&limite=15"}

@app.post("/buscar-produtos/")
def buscar(termo: str = Query(...), limite: int = Query(15)):
    buscar_produtos(termo, limite=limite)
    return {"mensagem": f"Busca por '{termo}' concluída. Produtos salvos no banco (limite: {limite})."}

@app.get("/produtos/", response_model=List[ProdutoSchema])
def listar_produtos(db: Session = Depends(get_db)):
    produtos = db.query(Produto).all()
    return produtos

@app.get("/melhor-preco/", response_model=List[ProdutoSchema])
def melhores_precos(limite: int = Query(10, ge=1), db: Session = Depends(get_db)):
    produtos = db.query(Produto).order_by(asc(Produto.preco)).limit(limite).all()
    return produtos

@app.get("/melhor-avaliados/", response_model=List[ProdutoSchema])
def melhores_avaliados(limite: int = Query(10, ge=1), db: Session = Depends(get_db)):
    produtos = (
        db.query(Produto)
        .filter(Produto.avaliacao != None, Produto.num_avaliacao != None)
        .order_by(desc(Produto.avaliacao), desc(Produto.num_avaliacao))
        .limit(limite)
        .all()
    )
    return produtos

@app.get("/melhores-custo-avaliativo/", response_model=List[ProdutoSchema])
def melhores_custo_avaliativo(limite: int = Query(10, ge=1), db: Session = Depends(get_db)):
    produtos = (
        db.query(Produto)
        .order_by(desc(Produto.avaliacao), asc(Produto.preco))
        .limit(limite)
        .all()
    )
    return produtos

# Listando as buscas realizadas
@app.get("/buscas/", response_model=List[BuscaSchema])
def listar_buscas(db: Session = Depends(get_db)):
    buscas = db.query(Busca).all()
    return buscas

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)


@app.delete("/limpar-banco")
def limpar_banco(termo: str = Query(...), db: Session = Depends(get_db)):
    if termo.lower() == "tudo":
        total_produtos = db.query(Produto).delete()
        db.commit()

        # Apagar buscas órfãs manualmente com acesso ao relacionamento
        buscas = db.query(Busca).all()
        total_buscas_removidas = 0
        for busca in buscas:
            if not busca.produtos:
                db.delete(busca)
                total_buscas_removidas += 1
        db.commit()

        return {
            "mensagem": f"{total_produtos} produtos removidos. {total_buscas_removidas} buscas órfãs também apagadas."
        }

    # Buscar a entrada na tabela Busca
    busca = db.query(Busca).filter(Busca.termo == termo).first()

    if not busca:
        return {"mensagem": f"Nenhuma busca com o termo '{termo}' foi encontrada."}

    total_produtos = db.query(Produto).filter(Produto.busca_id == busca.id).delete()
    db.commit()

    # Apagar a busca se ela ficou sem produtos
    db.refresh(busca)  # atualiza o estado da busca
    if not busca.produtos:
        db.delete(busca)
        db.commit()
        return {"mensagem": f"{total_produtos} produtos e a busca '{termo}' foram removidos."}

    return {"mensagem": f"{total_produtos} produtos com o termo '{termo}' foram removidos."}




