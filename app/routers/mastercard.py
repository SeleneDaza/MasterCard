from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import TarjetaMastercard
from datetime import date

router = APIRouter()

@router.post("/verificar-tarjeta")
def verificar_tarjeta(numero_tarjeta: str, cvv: str, fecha_expiracion: date, db: Session = Depends(get_db)):
    tarjeta = db.query(TarjetaMastercard).filter(
        TarjetaMastercard.numero_tarjeta == numero_tarjeta,
        TarjetaMastercard.cvv == cvv,
        TarjetaMastercard.fecha_expiracion == fecha_expiracion
    ).first()

    if tarjeta:
        return {"existe": True, "mensaje": "Tarjeta Mastercard verificada", "titular_verificado": True}

    return {"existe": False, "mensaje": "Tarjeta Mastercard no encontrada", "titular_verificado": False}