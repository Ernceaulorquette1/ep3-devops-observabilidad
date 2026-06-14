#!/usr/bin/env bash
# ============================================================
# Script de auditoria de cumplimiento (IE5)
# Verifica condiciones minimas de seguridad/calidad de forma local
# y devuelve exit-code != 0 si algo no cumple (util en pre-commit o CI).
# ============================================================
set -euo pipefail

ERRORES=0

echo ">> [1/4] Verificando que el contenedor NO corra como root..."
if grep -q "USER appuser" Dockerfile; then
  echo "   OK: usuario no-root definido."
else
  echo "   FALLA: el Dockerfile no define un usuario no-root."
  ERRORES=$((ERRORES+1))
fi

echo ">> [2/4] Verificando healthcheck en el Dockerfile..."
if grep -q "HEALTHCHECK" Dockerfile; then
  echo "   OK: healthcheck presente."
else
  echo "   FALLA: falta HEALTHCHECK."
  ERRORES=$((ERRORES+1))
fi

echo ">> [3/4] Verificando que existan pruebas automatizadas..."
if ls tests/test_*.py >/dev/null 2>&1; then
  echo "   OK: se encontraron pruebas."
else
  echo "   FALLA: no hay pruebas en tests/."
  ERRORES=$((ERRORES+1))
fi

echo ">> [4/4] Buscando posibles secretos hardcodeados..."
if grep -rEn "(password|secret|token)\s*=\s*['\"][^'\"]+['\"]" app/ 2>/dev/null | grep -vi "field\|secret_name"; then
  echo "   ADVERTENCIA: posibles secretos en el codigo (revisar)."
  ERRORES=$((ERRORES+1))
else
  echo "   OK: no se detectaron secretos evidentes."
fi

echo "------------------------------------------------------------"
if [ "$ERRORES" -gt 0 ]; then
  echo "AUDITORIA FALLIDA: $ERRORES hallazgo(s). El pipeline deberia detenerse."
  exit 1
fi
echo "AUDITORIA OK: todas las verificaciones pasaron."
