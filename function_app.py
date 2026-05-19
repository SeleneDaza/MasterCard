import azure.functions as func
import psycopg2
import json
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="verificar-tarjeta", methods=["POST"])
def verificar_tarjeta(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Mastercard verification request received.")

    try:
        data = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"exists": False, "message": "Invalid JSON body", "holder_verified": False}),
            mimetype="application/json",
            status_code=400
        )

    card_number = data.get("card_number")
    cvv = data.get("cvv")

    if not card_number or not cvv:
        return func.HttpResponse(
            json.dumps({"exists": False, "message": "Required fields: card_number, cvv", "holder_verified": False}),
            mimetype="application/json",
            status_code=400
        )

    conn = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5435,
            dbname="mastercard_db",
            user="mc_user",
            password="mc123"
        )
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM tarjetas_mastercard WHERE cvv = %s", (cvv,))
        cvv_exists = cur.fetchone() is not None
        logging.info(f"CVV check: {cvv_exists}")

        if not cvv_exists:
            cur.close()
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

        logging.info(f"Card verification completed: exists={exists}")
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
        logging.error(f"Unexpected error: {type(e).__name__}: {e}")
        return func.HttpResponse(
            json.dumps({"exists": False, "message": "Internal service error", "holder_verified": False}),
            mimetype="application/json",
            status_code=500
        )
    finally:
        if conn:
            conn.close()