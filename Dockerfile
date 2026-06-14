# ============================================================
# Dockerfile multi-etapa - Microservicio EP3 (heredado de EP2)
# Imagen slim + usuario no-root + healthcheck (buenas practicas IE2)
# ============================================================
FROM python:3.12-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

# Copia dependencias ya compiladas desde la etapa build
COPY --from=build /install /usr/local
COPY app ./app

# Usuario no-root por seguridad
RUN useradd -m appuser
USER appuser

EXPOSE 8000

# Healthcheck a nivel de contenedor (complementa las probes de K8s)
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
