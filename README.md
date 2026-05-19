# Mastercard Function — Serverless

Función serverless desarrollada con Azure Functions y Python que verifica
si una tarjeta Mastercard existe en la base de datos.

## Tecnologías
- Python 3.13
- Azure Functions Core Tools v4
- PostgreSQL (Docker)

## Requisitos previos
- Python 3.13
- Docker Desktop
- Node.js v18+
- Azure Functions Core Tools v4:
  npm install -g azure-functions-core-tools@4 --unsafe-perm true

## Configuración

1. Clona el repositorio
2. Instala dependencias:
   pip install --target=".python_packages/lib/site-packages" psycopg2-binary azure-functions

## Ejecución

### 1. Levanta la base de datos
   docker-compose up

### 2. Crea la tabla (solo primera vez)
   docker exec -it mastercard-mastercard-db-1 psql -U mc_user -d mastercard_db -c "CREATE TABLE tarjetas_mastercard (id SERIAL PRIMARY KEY, numero_tarjeta VARCHAR(16) NOT NULL UNIQUE, cvv VARCHAR(3) NOT NULL, fecha_expiracion DATE NOT NULL);"

### 3. Inserta datos de prueba (solo primera vez)
   docker exec -it mastercard-mastercard-db-1 psql -U mc_user -d mastercard_db -c "INSERT INTO tarjetas_mastercard (numero_tarjeta, cvv, fecha_expiracion) VALUES ('5111111111111111', '123', '2027-01-01'), ('5222222222222222', '456', '2026-06-15'), ('5333333333333333', '789', '2028-12-31');"

### 4. Levanta la función
   func start --port 7072

La función estará disponible en: http://localhost:7072/api/verificar-tarjeta

## Endpoint

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /api/verificar-tarjeta | Verifica si una tarjeta Mastercard existe |

### Body JSON
```json
{
  "numero_tarjeta": "5111111111111111",
  "cvv": "123",
  "fecha_expiracion": "01/27"
}
```

### Respuesta exitosa
```json
{
  "existe": true,
  "mensaje": "Tarjeta Mastercard verificada",
  "titular_verificado": true
}
```

### Respuesta fallida
```json
{
  "existe": false,
  "mensaje": "Tarjeta Mastercard no encontrada",
  "titular_verificado": false
}
```

## Diferencias con Servicio Visa

| Campo | Visa | Mastercard |
|-------|------|------------|
| numero_tarjeta | ✅ | ✅ |
| cvv | 3-4 dígitos | 3 dígitos |
| fecha_expiracion | ❌ | ✅ MM/AA |

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| DATABASE_URL | URL de conexión a PostgreSQL |

## Prueba rápida
curl -X POST http://localhost:7072/api/verificar-tarjeta \
  -H "Content-Type: application/json" \
  -d "{\"numero_tarjeta\": \"5111111111111111\", \"cvv\": \"123\", \"fecha_expiracion\": \"01/27\"}"