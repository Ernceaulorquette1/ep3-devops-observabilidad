# Informe — Evaluación Parcial N°3 (DOY0101)
## Observabilidad y entornos reales en DevOps

**Integrantes:** _________________________  /  _________________________
**Sección:** INGENIERIA DEVOPS_006V_OLS
**Fecha:** ______________
**Repositorio GitHub:** _________________________________________________

---

## 1. Introducción
Breve contexto del microservicio (heredado de la EP1/EP2) y objetivo de esta entrega.

> _Redactar por el equipo._

---

## 2. Herramientas de monitoreo y logging implementadas (IE1)
Descripción de Prometheus, la instrumentación del microservicio (`/metrics`), las
métricas de negocio personalizadas y el logging. Adjuntar **capturas** de:
- Prometheus → Status → Targets (mostrando el microservicio en estado `UP`).
- El endpoint `/metrics` respondiendo.

---

## 3. Despliegue en entorno orquestado (IE2)
Explicación del despliegue en Kubernetes: replicas, probes, límites de recursos,
ServiceMonitor y HPA. Adjuntar capturas de `kubectl get pods` y del servicio corriendo.

---

## 4. Dashboard de métricas clave (IE3)
Descripción del dashboard de Grafana y las métricas elegidas (throughput, latencia,
errores, CPU/memoria, cobertura, tiempo de despliegue). Adjuntar **captura del dashboard**.

---

## 5. Integración en el pipeline CI/CD (IE4)
Cómo se integran monitoreo, métricas y seguridad en el pipeline y cómo apoyan la toma
de decisiones. (Apoyarse en el README sección 4.)

> ⚠️ La *justificación técnica* de por qué eligieron estas herramientas y métricas
> debe redactarla el equipo, **sin IA** (pauta pág. 3).

---

## 6. Políticas de cumplimiento y auditoría (IE5)
SonarCloud (Quality Gate), Snyk, branch protection rules y `scripts/audit.sh`.
Adjuntar captura de las branch protection rules y del análisis de Sonar.

---

## 7. Demostración de detención del pipeline (IE6)
Evidencia de que ante una falla crítica el pipeline se detiene. Adjuntar **captura del
job en rojo (❌)** tras introducir a propósito una vulnerabilidad/baja de cobertura,
y explicación de qué mecanismo lo detuvo.

---

## 8. Conclusiones
> ⚠️ **Prohibido el uso de IA en esta sección** (pauta pág. 3). Redactar el equipo.

---

## 9. Reflexiones individuales
> ⚠️ **Obligatorias y sin IA.** Cada integrante escribe su aprendizaje y contribución.

**Integrante 1:** _________________________________________________

**Integrante 2:** _________________________________________________

---

## 10. Declaración de uso de Inteligencia Artificial
Según la pauta, se declara el uso de IA en este trabajo:

| Herramienta de IA | ¿Para qué se usó? | Secciones |
|---|---|---|
| (ej.) Claude | Andamiaje de código del pipeline, Dockerfile, manifiestos K8s y configuración de Prometheus/Grafana; redacción del README técnico | Código del repo, README, docs |
| | | |

> Las conclusiones, justificaciones técnicas y reflexiones individuales fueron
> redactadas por el equipo sin asistencia de IA.
> Referencia de citación: https://bibliotecas.duoc.cl/ia
