"""
Metricas de negocio personalizadas (IE1 / IE3)
==============================================
Estas metricas se exponen junto con las metricas HTTP automaticas en /metrics
y luego se grafican en el dashboard de Grafana.

  - items_creados_total : contador de items creados (volumen de negocio)
  - errores_negocio_total : contador de errores 4xx logicos (para alertar)
  - operacion_negocio_segundos : histograma de latencia de la logica de negocio
"""
from prometheus_client import Counter, Histogram

ITEMS_CREADOS = Counter(
    "items_creados_total",
    "Numero total de items creados en el microservicio",
)

ERRORES_NEGOCIO = Counter(
    "errores_negocio_total",
    "Numero total de errores de negocio (recurso no encontrado, validacion, etc.)",
)

LATENCIA_NEGOCIO = Histogram(
    "operacion_negocio_segundos",
    "Latencia de la logica de negocio en segundos",
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
)


def registrar_latencia_negocio(segundos: float) -> None:
    """Registra la duracion de una operacion de negocio en el histograma."""
    LATENCIA_NEGOCIO.observe(segundos)
