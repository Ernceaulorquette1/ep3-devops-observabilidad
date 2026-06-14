# Microservicio EP3 — Observabilidad y entornos reales en DevOps

Extensión del pipeline DevOps de la EP2, incorporando **observabilidad** (monitoreo, logging y métricas), **dashboards** y **validación de cumplimiento normativo** dentro del ciclo CI/CD.

> Asignatura: Ingeniería DevOps (DOY0101) · Evaluación Parcial N°3 (30%) · Trabajo en parejas

---

## 1. ¿Qué hace este proyecto?

| Componente | Herramienta | Indicador |
|---|---|---|
| Monitoreo, logs y métricas | **Prometheus** + instrumentación FastAPI | IE1 |
| Despliegue orquestado | **Kubernetes** (probes, recursos, HPA, ServiceMonitor) | IE2 |
| Dashboard de métricas clave | **Grafana** | IE3 |
| Documentación de integración | Este README + `docs/` | IE4 |
| Cumplimiento y auditoría | **SonarCloud** + **Snyk** + `scripts/audit.sh` + branch protection | IE5 |
| Pipeline que se detiene ante fallas | Quality Gate + **Trivy** con `exit-code: 1` | IE6 |

---

## 2. Estructura del repositorio

```
.
├── app/                      # Microservicio FastAPI instrumentado (Prometheus)
│   ├── main.py               # Endpoints + /metrics + logging
│   └── metrics.py            # Métricas de negocio personalizadas
├── tests/                    # Pruebas automatizadas (pytest + cobertura)
├── monitoring/
│   ├── prometheus/           # Config de scrape + reglas de alerta
│   └── grafana/              # Datasource + dashboard provisionado
├── k8s/                      # Manifiestos Kubernetes (app, prometheus, grafana)
├── scripts/audit.sh          # Auditoría de cumplimiento local
├── .github/
│   ├── workflows/ci-cd.yml   # Pipeline completo
│   └── dependabot.yml        # Actualización de dependencias
├── docs/                     # Diagrama y explicación de arquitectura
├── Dockerfile                # Multi-etapa, no-root, healthcheck
├── docker-compose.yml        # Stack local: app + Prometheus + Grafana
├── sonar-project.properties  # Configuración SonarCloud
├── INFORME.md                # Informe (secciones a completar por el equipo)
└── README.md
```

---

## 3. Cómo levantar todo en local (entorno simulado)

```bash
docker compose up --build
```

Luego abre:

| Servicio | URL | Notas |
|---|---|---|
| Microservicio | http://localhost:8000 | API |
| Métricas (Prometheus) | http://localhost:8000/metrics | lo que scrapea Prometheus |
| Prometheus | http://localhost:9090 | Status → Targets para ver el scrape |
| Grafana | http://localhost:3000 | usuario `admin` / clave `admin` |

En Grafana el dashboard **"Microservicio EP3 - Observabilidad"** ya viene cargado. Para generar tráfico y ver datos:

```bash
curl -X POST http://localhost:8000/items -H "Content-Type: application/json" -d '{"nombre":"Producto","precio":1990}'
curl http://localhost:8000/items/999   # genera un error de negocio (404)
```

---

## 4. Integración en el pipeline CI/CD (IE4)

El pipeline (`.github/workflows/ci-cd.yml`) ejecuta esta secuencia, y **cada etapa que falla detiene las siguientes**:

1. **`test`** → corre `pytest --cov=app` y publica la cobertura. *Métrica que decide si el código está suficientemente probado.*
2. **`calidad`** → SonarCloud analiza el código y evalúa el **Quality Gate**. Si no se cumplen los umbrales (cobertura, code smells, vulnerabilidades, duplicación), el job falla → **el pipeline se detiene** (IE5/IE6).
3. **`seguridad-dependencias`** → Snyk escanea dependencias; con `--severity-threshold=high` detiene el build si hay vulnerabilidades altas (IE5).
4. **`build-y-scan`** → construye la imagen y **Trivy** la escanea. Con `exit-code: 1` y `severity: CRITICAL,HIGH`, un CVE crítico **rompe el pipeline** (IE6).
5. **`deploy`** → solo si todo lo anterior pasó y estamos en `main`: build & push de la imagen, `kubectl apply` y publicación del **tiempo de despliegue** y la **cobertura** hacia Prometheus (alimenta el dashboard, IE3).

### Cómo esto apoya la toma de decisiones técnicas
- Las **alertas de Prometheus** (`alert.rules.yml`) avisan caída de servicio, exceso de errores 5xx y latencia alta → permiten decidir rollback o escalado.
- El **dashboard de Grafana** muestra CPU/memoria, throughput, errores, cobertura y tiempo de despliegue en un solo lugar → base objetiva para decidir optimizaciones o ajustar el HPA.
- El **Quality Gate** convierte la calidad en una condición *bloqueante*, no opcional → impide que código inseguro llegue a producción simulada.

---

## 5. Demostración de que el pipeline se detiene (IE6)

Tres mecanismos independientes detienen el pipeline ante una falla crítica:

1. **Quality Gate de Sonar**: si bajas la cobertura o introduces una vulnerabilidad, el job `calidad` falla.
2. **Snyk / Trivy**: una dependencia o imagen con CVE `HIGH`/`CRITICAL` hace fallar el escaneo (`exit-code: 1`).
3. **`scripts/audit.sh`**: verificación local que retorna error si falta el usuario no-root, el healthcheck, las pruebas o si hay secretos hardcodeados.

> Para evidenciarlo en el informe: inserta a propósito una dependencia vulnerable o baja el umbral de cobertura, corre el pipeline y captura el screenshot del job en rojo (❌). Revierte después.

---

## 6. Configuración previa (una sola vez)

1. **Secrets de GitHub** (Settings → Secrets and variables → Actions):
   - `SONAR_TOKEN` (de SonarCloud)
   - `SNYK_TOKEN` (de Snyk)
2. **SonarCloud**: crear el proyecto y completar `sonar-project.properties` con tu `organization` y `projectKey`.
3. **Branch protection** (IE5): ver `docs/arquitectura-observabilidad.md`.
4. Reemplaza `USUARIO` en `k8s/deployment.yaml` por tu usuario/organización de GHCR.

---

## 7. Declaración de uso de IA

Ver sección correspondiente en `INFORME.md`. Todo uso de IA se declara y cita según
la pauta del curso (https://bibliotecas.duoc.cl/ia).
