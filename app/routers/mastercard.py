from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import TarjetaMastercard
from datetime import date

router = APIRouter()

class TarjetaRequest(BaseModel):
    numero_tarjeta: str
    cvv: str
    fecha_expiracion: str  # formato MM/AA

@router.post("/verificar-tarjeta")
def verificar_tarjeta(request: TarjetaRequest, db: Session = Depends(get_db)):
    try:
        mes, anio = request.fecha_expiracion.split("/")
        fecha = date(int(f"20{anio}"), int(mes), 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha invalido. Use MM/AA")

    tarjeta = db.query(TarjetaMastercard).filter(
        TarjetaMastercard.numero_tarjeta == request.numero_tarjeta,
        TarjetaMastercard.cvv == request.cvv,
        TarjetaMastercard.fecha_expiracion == fecha
    ).first()

    if tarjeta:
        return {"existe": True, "mensaje": "Tarjeta Mastercard verificada", "titular_verificado": True}

    return {"existe": False, "mensaje": "Tarjeta Mastercard no encontrada", "titular_verificado": False}