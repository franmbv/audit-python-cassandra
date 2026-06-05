import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone
from typing import Optional

from main import app
from app.schemas.obras_schema import ObrasSchema
from app.schemas.seguridad_schema import SeguridadSchema
from app.schemas.membresias_schema import CodigoMembresiaSchema

@pytest.fixture
def mock_obras_repo(monkeypatch):
    class MockObrasRepositorio:
        async def registrar_cambio_estatus(self, datos):
            pass
        
        async def obtener_historial(self, id_obra: int):
            if id_obra == 1001:
                return [
                    ObrasSchema(
                        id_obra=1001,
                        fecha_evento=datetime.now(timezone.utc),
                        estatus_anterior="Disponible",
                        estatus_nuevo="Reservada",
                        usuario_id=1,
                        ip_origen="192.168.1.10"
                    )
                ]
            return []
    
    monkeypatch.setattr("app.routes.obras_routes.repo", MockObrasRepositorio())

@pytest.fixture
def mock_seguridad_repo(monkeypatch):
    class MockSeguridadRepositorio:
        async def insertar_log(self, datos):
            pass
            
        async def obtener_logs_por_usuario(self, login_usuario: str, desde: datetime, hasta: datetime):
            if login_usuario == "admin":
                return [
                    SeguridadSchema(
                        login_usuario="admin",
                        fecha_evento=datetime.now(timezone.utc),
                        evento_tipo="LOGIN_EXITOSO",
                        ip_origen="192.168.1.10",
                        detalles="Ingreso al sistema",
                        usuario_id=1
                    )
                ]
            return []

    monkeypatch.setattr("app.routes.seguridad_routes.repo", MockSeguridadRepositorio())

@pytest.fixture
def mock_membresias_repo(monkeypatch):
    class MockMembresiasRepositorio:
        async def insertar_codigo(self, datos):
            return datos
        
        async def obtener_codigos_por_comprador(self, id_comprador: int, page_size: int = 20, paging_state: Optional[str] = None):
            if id_comprador == 5001:
                return [
                    CodigoMembresiaSchema(
                        id_comprador=5001,
                        fecha_registro=datetime.now(timezone.utc),
                        codigo_seguridad="SECRET123",
                        correo_envio="test@example.com",
                        estado="EMITIDO"
                    )
                ], None
            return [], None

    monkeypatch.setattr("app.routes.membresias_routes.repo", MockMembresiasRepositorio())

@pytest.mark.asyncio
async def test_registrar_evento_obra(mock_obras_repo):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "id_obra": 1001,
            "fecha_evento": datetime.now(timezone.utc).isoformat(),
            "estatus_anterior": "Disponible",
            "estatus_nuevo": "Reservada",
            "usuario_id": 1,
            "ip_origen": "192.168.1.10"
        }
        response = await client.post("/obras/historico", json=payload)
        assert response.status_code == 201
        assert response.json() == {"mensaje": "Historial de cambio de estatus registrado con éxito"}

@pytest.mark.asyncio
async def test_obtener_historial_obra(mock_obras_repo):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/obras/historico/1001")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id_obra"] == 1001
        assert data[0]["estatus_nuevo"] == "Reservada"

@pytest.mark.asyncio
async def test_obtener_historial_obra_no_encontrada(mock_obras_repo):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/obras/historico/9999")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_registrar_log_seguridad(mock_seguridad_repo):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "login_usuario": "admin",
            "fecha_evento": datetime.now(timezone.utc).isoformat(),
            "evento_tipo": "LOGIN_EXITOSO",
            "ip_origen": "192.168.1.10",
            "detalles": "Ingreso al sistema",
            "usuario_id": 1
        }
        response = await client.post("/seguridad/logs", json=payload)
        assert response.status_code == 201

@pytest.mark.asyncio
async def test_obtener_logs_seguridad(mock_seguridad_repo):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/seguridad/logs?login_usuario=admin&desde=2023-01-01T00:00:00Z&hasta=2024-12-31T23:59:59Z")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["login_usuario"] == "admin"

@pytest.mark.asyncio
async def test_registrar_codigo_membresia(mock_membresias_repo):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "id_comprador": 5001,
            "fecha_registro": datetime.now(timezone.utc).isoformat(),
            "codigo_seguridad": "SECRET123",
            "correo_envio": "test@example.com",
            "estado": "EMITIDO"
        }
        response = await client.post("/membresias/codigos", json=payload)
        assert response.status_code == 201
        assert response.json()["mensaje"] == "Codigo de membresia insertado"

@pytest.mark.asyncio
async def test_obtener_codigos_membresia(mock_membresias_repo):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/membresias/codigos?id_comprador=5001")
        assert response.status_code == 200
        data = response.json()
        assert len(data["datos"]) == 1
        assert data["datos"][0]["id_comprador"] == 5001
