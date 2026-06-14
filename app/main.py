"""
Microservicio EP3 - DevOps (Observabilidad)
===========================================
Extiende el microservicio de la EP2 incorporando:
  - Instrumentación Prometheus (métricas HTTP automáticas + endpoint /metrics)  -> IE1
  - Métricas de negocio personalizadas (errores, items creados)                 -> IE1 / IE3
  - Logging estructurado para observar el comportamiento en ejecución           -> IE1
  - Endpoint /health para probes de Kubernetes (liveness/readiness)             -> IE2

NOTA: Reemplaza la lógica interna (modelo Item, endpoints) por la de tu
microservicio real de la EP1. La instrumentación y el endpoint /metrics
funcionan igual sin importar el dominio del servicio.
"""
import logging
import time
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator

from app.metrics import ITEMS_CREADOS, ERRORES_NEGOCIO, registrar_latencia_negocio

# ---------------------------------------------------------------------------
# Logging estructurado (IE1): cada request y evento relevante queda registrado.
# En produccion estos logs los recoge Prometheus/Loki o CloudWatch.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
)
logger = logging.getLogger("microservicio-ep3")

app = FastAPI(
    title="Microservicio EP3 DevOps - Observabilidad",
    description="Microservicio con monitoreo Prometheus, dashboards Grafana y CI/CD",
    version="2.0.0",
)

# ---------------------------------------------------------------------------
# Instrumentacion Prometheus (IE1)
# Expone automaticamente el endpoint /metrics con metricas como:
#   http_requests_total, http_request_duration_seconds, etc.
# Estas son las que Prometheus "scrapea" y Grafana grafica.
# ---------------------------------------------------------------------------
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# "Base de datos" en memoria (solo demostracion).
_items: Dict[int, "Item"] = {}
_next_id = 1


class Item(BaseModel):
    id: int | None = None
    nombre: str = Field(..., min_length=1, max_length=100)
    precio: float = Field(..., ge=0)


@app.get("/", tags=["sistema"])
def root():
    logger.info("Acceso a la raiz del servicio")
    return {"servicio": "EP3 DevOps Observabilidad", "version": "2.0.0", "estado": "ok"}


@app.get("/health", tags=["sistema"])
def health():
    """Healthcheck para probes de Docker y Kubernetes (IE2)."""
    return {"status": "healthy"}


@app.get("/items", tags=["items"])
def listar_items():
    logger.info("Listado de items solicitado (total=%d)", len(_items))
    return list(_items.values())


@app.post("/items", status_code=201, tags=["items"])
def crear_item(item: Item):
    global _next_id
    inicio = time.perf_counter()
    item.id = _next_id
    _items[_next_id] = item
    _next_id += 1

    # Metrica de negocio personalizada (IE1 / IE3)
    ITEMS_CREADOS.inc()
    registrar_latencia_negocio(time.perf_counter() - inicio)

    logger.info("Item creado id=%d nombre=%s", item.id, item.nombre)
    return item


@app.get("/items/{item_id}", tags=["items"])
def obtener_item(item_id: int):
    if item_id not in _items:
        # Metrica de errores de negocio (IE1): permite alertar cuando suben.
        ERRORES_NEGOCIO.inc()
        logger.warning("Item no encontrado id=%d", item_id)
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return _items[item_id]


@app.delete("/items/{item_id}", status_code=204, tags=["items"])
def eliminar_item(item_id: int):
    if item_id not in _items:
        ERRORES_NEGOCIO.inc()
        raise HTTPException(status_code=404, detail="Item no encontrado")
    del _items[item_id]
    logger.info("Item eliminado id=%d", item_id)
