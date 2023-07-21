from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class HabilitarTransporteEgreso(Base):
    __tablename__ = 'habilitar_transporte_egreso'

    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer)
    patente = Column(String(255), nullable=False)