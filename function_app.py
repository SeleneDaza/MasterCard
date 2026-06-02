import azure.functions as func
import psycopg2
import json
import logging
import os
import time
from pathlib import Path

import csv_logger

Path("logs").mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="verificar-tarjeta", methods=["POST"])
def verificar_tarjeta(req: func.HttpRequest) -> func.HttpResponse:
    client_ip = req.headers.get("X-Forwarded-For", req.headers.get("Client-IP", ""))
    module = "function_app.verificar_tarjeta"

    try:
        data = req.get_json()
    except ValueError:
        csv_logger.write_log("ERROR", "CARD_VERIFICATION_ERROR", module, client_ip, "FAILED",
                             error_code="INVALID_JSON", message="Invalid JSON body")
        return func.HttpResponse(
            json.dumps({"exists": False, "message": "Invalid JSON body", "holder_verified": False}),
            mimetype="application/json",
            status_code=400
        )

    card_number = data.get("card_number")
    cvv = data.get("cvv")
    last4 = str(card_number)[-4:] if card_number else "????"

    csv_logger.write_log("INFO", "CARD_VERIFICATION_RECEIVED", module, client_ip, "STARTED",
                         message=f"Verification request received, last4={last4}")

    if not card_number or not cvv:
        csv_logger.write_log("ERROR", "CARD_VERIFICATION_ERROR", module, client_ip, "FAILED",
                             error_code="MISSING_FIELDS", message="Required fields: card_number, cvv")
        return func.HttpResponse(
            json.dumps({"exists": False, "message": "Required fields: card_number, cvv", "holder_verified": False}),
            mimetype="application/json",
            status_code=400
        )

    conn = None
    start_time = time.monotonic()
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="mastercard_db",
            user="postgres",
            password="12345678"
        )
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM tarjetas_mastercard WHERE cvv = %s", (cvv,))
        cvv_exists = cur.fetchone() is not None

        if not cvv_exists:
            cur.close()
            duration_ms = int((time.monotonic() - start_time) * 1000)
            csv_logger.write_log("ERROR", "CARD_NOT_FOUND", module, client_ip, "FAILED",
                                 error_code="CARD_NOT_FOUND", duration_ms=duration_ms,
                                 message="Card not found")
            return func.HttpResponse(
                json.dumps({"exists": False, "message": "CVV not found", "holder_verified": False}),
                mimetype="application/json",
                status_code=200
            )

        cur.execute(
            "SELECT 1 FROM tarjetas_mastercard WHERE cvv = %s AND numero_tarjeta = %s",
            (cvv, card_number)
        )
        exists = cur.fetchone() is not None
        cur.close()
        duration_ms = int((time.monotonic() - start_time) * 1000)

        if exists:
            csv_logger.write_log("SUCCESS", "CARD_FOUND", module, client_ip, "SUCCESS",
                                 duration_ms=duration_ms, message="Card verified")
        else:
            csv_logger.write_log("ERROR", "CARD_NOT_FOUND", module, client_ip, "FAILED",
                                 error_code="CARD_NOT_FOUND", duration_ms=duration_ms,
                                 message="Card not found")

        return func.HttpResponse(
            json.dumps({
                "exists": exists,
                "message": "Mastercard verified successfully" if exists else "Card not found",
                "holder_verified": exists
            }),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        duration_ms = int((time.monotonic() - start_time) * 1000)
        logging.error(f"Unexpected error: {type(e).__name__}: {e}")
        csv_logger.write_log("ERROR", "CARD_VERIFICATION_ERROR", module, client_ip, "FAILED",
                             error_code="INTERNAL_ERROR", duration_ms=duration_ms,
                             message=f"Internal service error: {type(e).__name__}")
        return func.HttpResponse(
            json.dumps({"exists": False, "message": "Internal service error", "holder_verified": False}),
            mimetype="application/json",
            status_code=500
        )
    finally:
        if conn:
            conn.close()