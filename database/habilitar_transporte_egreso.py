from sqlalchemy import Column, Integer, String, Time, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class HabilitarTransporteEgreso(Base):
    __tablename__ = 'habilitar_transporte_egreso'
    id = Column(Integer, primary_key=True)
    patente = Column(String(255), nullable=False)
    fecha = Column(Date)
    hora = Column(Time)
    interno_id = Column(String(255), nullable=False)
