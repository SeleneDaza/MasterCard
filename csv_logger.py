import csv
import os
from datetime import datetime, timezone

LOG_PATH = os.path.join(os.path.dirname(__file__), "logs", "app.log")
FIELDS = [
    "timestamp", "log_id", "level", "event", "module",
    "transaction_id", "session_id", "user_id", "client_ip",
    "payment_provider", "status", "error_code", "duration_ms", "message",
]


def _next_log_id():
    if not os.path.exists(LOG_PATH):
        return 1
    with open(LOG_PATH, "r", newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.reader(f))


def write_log(level, event, module, client_ip, status,
              error_code="", duration_ms="", message=""):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    file_exists = os.path.exists(LOG_PATH)
    log_id = _next_log_id()

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond // 1000:03d}Z"

    row = {
        "timestamp": timestamp,
        "log_id": log_id,
        "level": level,
        "event": event,
        "module": module,
        "transaction_id": "",
        "session_id": "",
        "user_id": "",
        "client_ip": client_ip or "",
        "payment_provider": "mastercard",
        "status": status,
        "error_code": error_code or "",
        "duration_ms": duration_ms if duration_ms != "" else "",
        "message": message or "",
    }

    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
