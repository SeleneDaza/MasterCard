from fastapi import FastAPI
from app.routers import mastercard
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Servicio Mastercard", version="1.0.0")

app.include_router(mastercard.router, prefix="/mastercard", tags=["Mastercard"])