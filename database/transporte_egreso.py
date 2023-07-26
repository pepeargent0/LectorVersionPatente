from sqlalchemy import Column, Integer, String, Date, Time, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TransporteEgreso(Base):
    __tablename__ = 'transporte_egreso'

    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, nullable=True)
    empresa = Column(String(255), nullable=True)
    patente = Column(String(255), nullable=False)
    fecha_salida = Column(Date)
    hora_salida = Column(Time)
    lectura_forzada = Column(Boolean)
    procesado = Column(Boolean)
    motivo = Column(String(700), nullable=False)
    interno_id = Column(String(255), nullable=False)


