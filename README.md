# Servicio Mastercard - REST API

Microservicio independiente desarrollado en Python/FastAPI que verifica
si una tarjeta Mastercard existe en la base de datos.

## Tecnologías
- Python 3.13
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker / Docker Compose

## Estructura del proyecto
mastercard-service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   └── routers/
│       ├── __init__.py
│       └── mastercard.py
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
└── README.md

## Configuración

1. Clona el repositorio
2. Copia el archivo de variables de entorno:
cp .env.example .env
3. Edita `.env` con tus credenciales reales

## Ejecución con Docker

docker-compose up --build

El servicio estará disponible en: http://localhost:8001

## Endpoint

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /mastercard/verificar-tarjeta | Verifica si una tarjeta Mastercard existe |

### Parámetros
| Campo | Tipo | Descripción |
|-------|------|-------------|
| numero_tarjeta | string | Número de 16 dígitos |
| cvv | string | Código de seguridad de 3 dígitos |
| fecha_expiracion | date | Fecha de expiración (YYYY-MM-DD) |

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
| fecha_expiracion | ❌ | ✅ |

## Documentación interactiva
http://localhost:8001/docs