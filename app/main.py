"""
Microservicio EP3 - DevOps Observabilidad
=========================================

Incluye:
- FastAPI
- Prometheus /metrics
- Métricas personalizadas para Grafana
- Healthcheck para Docker y Kubernetes
- Logs estructurados
- Métricas simuladas de cobertura y tiempo de despliegue
"""

import logging
import random
import time
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from prometheus_client import Counter, Gauge, Histogram
from prometheus_fastapi_instrumentator import Instrumentator


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("microservicio-ep3")


# ============================================================
# APP FASTAPI
# ============================================================

app = FastAPI(
    title="Microservicio EP3 DevOps - Observabilidad",
    description="Microservicio con métricas Prometheus y dashboard Grafana",
    version="2.0.0",
)


# ============================================================
# MÉTRICAS PERSONALIZADAS PARA GRAFANA
# ============================================================

EP3_APP_STATUS = Gauge(
    "ep3_app_health_status",
    "Estado del microservicio. 1 = UP, 0 = DOWN"
)

EP3_ITEMS_CREADOS = Counter(
    "ep3_items_created_total",
    "Cantidad total de items creados"
)

EP3_ERRORES_NEGOCIO = Counter(
    "ep3_business_errors_total",
    "Cantidad total de errores de negocio"
)

EP3_REQUESTS_TOTAL = Counter(
    "ep3_http_requests_total",
    "Cantidad total de requests HTTP",
    ["method", "endpoint", "status_code"]
)

EP3_REQUEST_LATENCY = Histogram(
    "ep3_http_request_duration_seconds",
    "Duración de requests HTTP en segundos",
    ["method", "endpoint"]
)

EP3_VALOR_NEGOCIO = Gauge(
    "ep3_business_value_total",
    "Valor de negocio simulado para visualizar gráficos"
)

EP3_TEST_COVERAGE = Gauge(
    "test_coverage_percent",
    "Porcentaje de cobertura de pruebas automatizadas"
)

EP3_DEPLOY_TIME = Gauge(
    "deployment_time_seconds",
    "Tiempo de despliegue del pipeline en segundos"
)

EP3_PIPELINE_STATUS = Gauge(
    "pipeline_status",
    "Estado del pipeline. 1 = OK, 0 = FALLA"
)


# ============================================================
# INSTRUMENTACIÓN AUTOMÁTICA PROMETHEUS
# ============================================================

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


# ============================================================
# BASE DE DATOS EN MEMORIA
# ============================================================

_items: Dict[int, "Item"] = {}
_next_id = 1


class Item(BaseModel):
    id: Optional[int] = None
    nombre: str = Field(..., min_length=1, max_length=100)
    precio: float = Field(..., ge=0)


# ============================================================
# MIDDLEWARE PARA MÉTRICAS HTTP
# ============================================================

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    inicio = time.time()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response

    except Exception:
        status_code = 500
        raise

    finally:
        duracion = time.time() - inicio
        endpoint = request.url.path
        method = request.method

        EP3_REQUESTS_TOTAL.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()

        EP3_REQUEST_LATENCY.labels(
            method=method,
            endpoint=endpoint
        ).observe(duracion)


# ============================================================
# ENDPOINTS DEL SISTEMA
# ============================================================

@app.get("/", tags=["sistema"])
def root():
    EP3_APP_STATUS.set(1)
    EP3_TEST_COVERAGE.set(85)
    EP3_DEPLOY_TIME.set(42)
    EP3_PIPELINE_STATUS.set(1)

    logger.info("Acceso a la raíz del servicio")

    return {
        "servicio": "EP3 DevOps Observabilidad",
        "version": "2.0.0",
        "estado": "ok",
        "metricas": "/metrics",
        "health": "/health",
        "grafana": "http://localhost:3001",
        "prometheus": "http://localhost:9090"
    }


@app.get("/health", tags=["sistema"])
def health():
    """
    Healthcheck para Docker y Kubernetes.
    También actualiza métricas simuladas de calidad.
    """
    EP3_APP_STATUS.set(1)
    EP3_TEST_COVERAGE.set(85)
    EP3_DEPLOY_TIME.set(42)
    EP3_PIPELINE_STATUS.set(1)

    return {
        "status": "healthy",
        "service": "microservicio-ep3",
        "test_coverage": "85%",
        "deployment_time_seconds": 42,
        "pipeline_status": "OK"
    }


@app.get("/quality", tags=["sistema"])
def quality():
    """
    Endpoint para exponer métricas simuladas de calidad del pipeline.
    """
    EP3_TEST_COVERAGE.set(85)
    EP3_DEPLOY_TIME.set(42)
    EP3_PIPELINE_STATUS.set(1)

    return {
        "test_coverage_percent": 85,
        "deployment_time_seconds": 42,
        "pipeline_status": "OK"
    }


# ============================================================
# ENDPOINTS DE ITEMS
# ============================================================

@app.get("/items", tags=["items"])
def listar_items():
    logger.info("Listado de items solicitado. Total=%d", len(_items))

    EP3_VALOR_NEGOCIO.set(len(_items))

    return list(_items.values())


@app.post("/items", status_code=201, tags=["items"])
def crear_item(item: Item):
    global _next_id

    item.id = _next_id
    _items[_next_id] = item
    _next_id += 1

    EP3_ITEMS_CREADOS.inc()
    EP3_VALOR_NEGOCIO.set(len(_items))

    logger.info(
        "Item creado id=%d nombre=%s precio=%s",
        item.id,
        item.nombre,
        item.precio
    )

    return item


@app.get("/items/{item_id}", tags=["items"])
def obtener_item(item_id: int):
    if item_id not in _items:
        EP3_ERRORES_NEGOCIO.inc()
        logger.warning("Item no encontrado id=%d", item_id)

        raise HTTPException(
            status_code=404,
            detail="Item no encontrado"
        )

    return _items[item_id]


@app.delete("/items/{item_id}", status_code=204, tags=["items"])
def eliminar_item(item_id: int):
    if item_id not in _items:
        EP3_ERRORES_NEGOCIO.inc()
        logger.warning("Intento de eliminar item inexistente id=%d", item_id)

        raise HTTPException(
            status_code=404,
            detail="Item no encontrado"
        )

    del _items[item_id]
    EP3_VALOR_NEGOCIO.set(len(_items))

    logger.info("Item eliminado id=%d", item_id)


# ============================================================
# ENDPOINTS PARA GENERAR DATOS EN GRAFANA
# ============================================================

@app.get("/load-test", tags=["observabilidad"])
def load_test():
    """
    Genera actividad para que Grafana muestre gráficos.
    """
    global _next_id

    cantidad = random.randint(1, 5)

    for _ in range(cantidad):
        item = Item(
            id=_next_id,
            nombre=f"Producto-{_next_id}",
            precio=random.randint(1000, 50000)
        )

        _items[_next_id] = item
        _next_id += 1

        EP3_ITEMS_CREADOS.inc()

    EP3_VALOR_NEGOCIO.set(len(_items))
    EP3_APP_STATUS.set(1)
    EP3_TEST_COVERAGE.set(85)
    EP3_DEPLOY_TIME.set(42)
    EP3_PIPELINE_STATUS.set(1)

    logger.info("Load test ejecutado. Items actuales=%d", len(_items))

    return {
        "message": "Datos generados correctamente",
        "items_creados_en_prueba": cantidad,
        "total_items": len(_items)
    }


@app.get("/simulate-error", tags=["observabilidad"])
def simulate_error():
    """
    Genera un error controlado para visualizar errores en Grafana.
    """
    EP3_ERRORES_NEGOCIO.inc()
    EP3_APP_STATUS.set(1)

    logger.error("Error simulado para observabilidad")

    raise HTTPException(
        status_code=500,
        detail="Error simulado para pruebas de observabilidad"
    )


@app.get("/simulate-pipeline-fail", tags=["observabilidad"])
def simulate_pipeline_fail():
    """
    Simula una falla crítica de pipeline para evidenciar control automático.
    """
    EP3_PIPELINE_STATUS.set(0)
    EP3_ERRORES_NEGOCIO.inc()

    logger.error("Pipeline simulado en estado FALLA")

    return {
        "pipeline_status": "FAILED",
        "message": "Falla simulada del pipeline para evidencia EP3"
    }


@app.get("/simulate-pipeline-ok", tags=["observabilidad"])
def simulate_pipeline_ok():
    """
    Devuelve el pipeline a estado correcto.
    """
    EP3_PIPELINE_STATUS.set(1)

    logger.info("Pipeline simulado en estado OK")

    return {
        "pipeline_status": "OK",
        "message": "Pipeline restaurado correctamente"
    }