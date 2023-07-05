from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TransporteVehiculos(Base):
    __tablename__ = 'transporte_vehiculos'

    id = Column(Integer, primary_key=True)
    codigo = Column(String(255))
    patente = Column(String(255), nullable=False)
    patenteSecundaria = Column(String(255))
    descripcion = Column(String(255))
    empresaId = Column(Integer)
    deleted = Column(Boolean, default=False)
    habilitado = Column(Boolean)
    habilitado_id = Column(String(255))

    def __repr__(self):
        return f"<TransporteVehiculos(id={self.id}, codigo='{self.codigo}', patente='{self.patente}', " \
               f"patenteSecundaria='{self.patenteSecundaria}', descripcion='{self.descripcion}', " \
               f"empresaId={self.empresaId}, deleted={self.deleted}, habilitado={self.habilitado}, " \
               f"habilitado_id='{self.habilitado_id}')>"
