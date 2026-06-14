"""
Pruebas automatizadas (alimentan la cobertura del dashboard - IE3)
==================================================================
Se ejecutan en el pipeline con: pytest --cov=app
La cobertura resultante se publica como metrica y se grafica en Grafana.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["estado"] == "ok"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_metrics_expuesto():
    """El endpoint /metrics debe existir para que Prometheus lo scrapee (IE1)."""
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text


def test_crear_y_obtener_item():
    r = client.post("/items", json={"nombre": "Producto Test", "precio": 1990})
    assert r.status_code == 201
    item_id = r.json()["id"]

    r2 = client.get(f"/items/{item_id}")
    assert r2.status_code == 200
    assert r2.json()["nombre"] == "Producto Test"


def test_item_inexistente_devuelve_404():
    r = client.get("/items/99999")
    assert r.status_code == 404


def test_listar_items():
    r = client.get("/items")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
