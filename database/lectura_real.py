from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LecturaReal(Base):
    __tablename__ = 'lectura_real'
    id = Column(Integer, primary_key=True, autoincrement=True)
    info = Column(String(255), nullable=False)
