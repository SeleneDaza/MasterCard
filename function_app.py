import azure.functions as func
import psycopg2
import json
import logging
import os
from datetime import date

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="verificar-tarjeta", methods=["POST"])
def verificar_tarjeta(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Solicitud de verificacion de tarjeta Mastercard recibida.")

    try:
        data = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"existe": False, "mensaje": "Body JSON invalido", "titular_verificado": False}),
            mimetype="application/json",
            status_code=400
        )

    numero_tarjeta = data.get("numero_tarjeta")
    cvv = data.get("cvv")
    fecha_expiracion = data.get("fecha_expiracion")

    if not numero_tarjeta or not cvv or not fecha_expiracion:
        return func.HttpResponse(
            json.dumps({"existe": False, "mensaje": "Campos requeridos: numero_tarjeta, cvv, fecha_expiracion", "titular_verificado": False}),
            mimetype="application/json",
            status_code=400
        )

    conn = None
    try:
        mes, anio = fecha_expiracion.split("/")
        fecha = date(int(f"20{anio}"), int(mes), 1)

        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM tarjetas_mastercard WHERE numero_tarjeta = %s AND cvv = %s AND fecha_expiracion = %s",
            (numero_tarjeta, cvv, fecha)
        )
        existe = cur.fetchone() is not None
        cur.close()

        logging.info(f"Verificacion completada: existe={existe}")
        return func.HttpResponse(
            json.dumps({
                "existe": existe,
                "mensaje": "Tarjeta Mastercard verificada" if existe else "Tarjeta Mastercard no encontrada",
                "titular_verificado": existe
            }),
            mimetype="application/json",
            status_code=200
        )
    except ValueError:
        logging.warning("Formato de fecha invalido")
        return func.HttpResponse(
            json.dumps({"existe": False, "mensaje": "Formato de fecha invalido. Use MM/AA", "titular_verificado": False}),
            mimetype="application/json",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Error al verificar tarjeta Mastercard: {e}")
        return func.HttpResponse(
            json.dumps({"existe": False, "mensaje": "Error interno del servicio", "titular_verificado": False}),
            mimetype="application/json",
            status_code=500
        )
    finally:
        if conn:
            conn.close()