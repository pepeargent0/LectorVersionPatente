from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Empresas(Base):
    __tablename__ = 'empresas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    razonSocial = Column(String(255), nullable=False)
    nombre = Column(String(255))
    tipoDocumento = Column(Integer, nullable=False)
    documento = Column(String(255), unique=True, nullable=False)
    tipoResponsabilidad = Column(Integer, nullable=False)
    # localidadId = Column(Integer, ForeignKey('localidades.id'))
    # localidad = relationship('Localidades')  # Establece la relación con la tabla 'localidades'
    direccion = Column(String(255))
    telefono = Column(String(255))
    email = Column(String(255))
    locked = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
