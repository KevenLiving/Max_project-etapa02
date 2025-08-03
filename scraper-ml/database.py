from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "sqlite:///./produtos.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Busca(Base):
    __tablename__ = "buscas"

    id = Column(Integer, primary_key=True, index=True)
    termo = Column(String, unique=True)

    produtos = relationship("Produto", back_populates="busca", cascade="all, delete-orphan")


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    preco = Column(Float)
    avaliacao = Column(Float)
    num_avaliacao = Column(Integer)
    link = Column(String)

    busca_id = Column(Integer, ForeignKey("buscas.id"))
    busca = relationship("Busca", back_populates="produtos")

Base.metadata.create_all(bind=engine)
