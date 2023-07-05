from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Localidades(Base):
    __tablename__ = 'localidades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    provinciaId = Column(Integer, nullable=False)
    nombre = Column(String(255), nullable=False)
    codigoPostal = Column(String(255), nullable=False)
    deleted = Column(Boolean, default=False)

    empresas = relationship('Empresas', backref='localidad')  # Establece la relación con la tabla 'empresas'
