from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class TarjetaMastercard(Base):
    __tablename__ = "tarjetas_mastercard"

    id = Column(Integer, primary_key=True, index=True)
    numero_tarjeta = Column(String(16), nullable=False, unique=True)
    cvv = Column(String(3), nullable=False)
    fecha_expiracion = Column(Date, nullable=False)