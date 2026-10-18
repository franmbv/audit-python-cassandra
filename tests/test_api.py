import pytest
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple
from httpx import AsyncClient, ASGITransport

from main import app
from app.domain.models.obra import ObraHistorial
from app.domain.models.seguridad import SeguridadLog
from app.domain.models.membresia import CodigoMembresia
from app.domain.models.reporte import ReporteFacturacion, ReporteMembresia
from app.domain.repositories.obra_repository import ObraRepository
from app.domain.repositories.seguridad_repository import SeguridadRepository
from app.domain.repositories.membresia_repository import MembresiaRepository
from app.domain.repositories.reporte_repository import ReporteRepository
from app.web.dependencies import (
    get_obra_repository,
    get_seguridad_repository,
    get_membresia_repository,
    get_reporte_repository,
)

COMPRADOR_TEST = 500


# --- Mock Repositories for Testing ---

class MockObraRepository(ObraRepository):
    async def create_historial(self, historial: ObraHistorial) -> None:
        pass

    async def get_historial_by_obra(self, id_obra: int) -> List[ObraHistorial]:
        if id_obra == 1001:
            return [
                ObraHistorial(
                    id_obra=1001,
                    fecha_evento=datetime.now(timezone.utc),
                    estatus_anterior="Disponible",
                    estatus_nuevo="Reservada",
                    usuario_id=1,
                    ip_origen="192.168.1.10",
                )
            ]
        return []


class MockSeguridadRepository(SeguridadRepository):
    async def create_log(self, log: SeguridadLog) -> None:
        pass

    async def get_logs_by_user(
        self, login_usuario: str, desde: datetime, hasta: datetime
    ) -> List[SeguridadLog]:
        if login_usuario == "admin":
            return [
                SeguridadLog(
                    login_usuario="admin",
                    fecha_evento=datetime.now(timezone.utc),
                    accion="LOGIN_EXITOSO",
                    ip_origen="192.168.1.10",
                    detalles="Ingreso al sistema",
                    usuario_id=1,
                )
            ]
        return []


class MockMembresiaRepository(MembresiaRepository):
    async def create_codigo(self, codigo: CodigoMembresia) -> CodigoMembresia:
        return codigo

    async def get_codigos_by_comprador(
        self,
        id_comprador: int,
        page_size: int = 20,
        paging_state: Optional[str] = None,
    ) -> Tuple[List[CodigoMembresia], Optional[str]]:
        if id_comprador == COMPRADOR_TEST:
            return [
                CodigoMembresia(
                    id_comprador=COMPRADOR_TEST,
                    fecha_registro=datetime.now(timezone.utc),
                    codigo_seguridad="SECRET123",
                    correo_envio="test@example.com",
                    estado="EMITIDO",
                )
            ], None
        return [], None


class MockReporteRepository(ReporteRepository):
    async def create_factura(self, reporte: ReporteFacturacion) -> None:
        pass

    async def get_reporte_facturacion(self, anio: int, mes: int) -> List[ReporteFacturacion]:
        if anio == 2025 and mes == 1:
            return [
                ReporteFacturacion(
                    anio=2025,
                    mes=1,
                    id_factura=1001,
                    fecha_emision=datetime.now(timezone.utc),
                    id_comprador=101,
                    monto_neto=Decimal("150.00"),
                    iva_calculado=Decimal("24.00"),
                    ganancia_museo=Decimal("45.00"),
                    estado="pagada",
                )
            ]
        return []

    async def create_membresia(self, reporte: ReporteMembresia) -> None:
        pass

    async def get_reporte_membresias(self, anio: int, mes: int) -> List[ReporteMembresia]:
        if anio == 2025 and mes == 1:
            return [
                ReporteMembresia(
                    anio=2025,
                    mes=1,
                    id_membresia=2001,
                    fecha_registro=datetime.now(timezone.utc),
                    id_comprador=101,
                    codigo_membresia="MEM-2025-A001",
                    monto_cobrado=Decimal("10.00"),
                    estado="activa",
                )
            ]
        return []


@pytest.fixture(autouse=True)
def override_dependencies():
    """Injects mocked repositories into FastAPI dependency container for testing."""
    app.dependency_overrides[get_obra_repository] = lambda: MockObraRepository()
    app.dependency_overrides[get_seguridad_repository] = lambda: MockSeguridadRepository()
    app.dependency_overrides[get_membresia_repository] = lambda: MockMembresiaRepository()
    app.dependency_overrides[get_reporte_repository] = lambda: MockReporteRepository()
    yield
    app.dependency_overrides.clear()


# --- Endpoint Integration Tests ---

@pytest.mark.asyncio
async def test_registrar_evento_obra():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "id_obra": 1001,
            "fecha_evento": datetime.now(timezone.utc).isoformat(),
            "estatus_anterior": "Disponible",
            "estatus_nuevo": "Reservada",
            "usuario_id": 1,
            "ip_origen": "192.168.1.10",
        }
        response = await client.post("/obras/historico", json=payload)
        assert response.status_code == 201
        assert response.json() == {"mensaje": "Historial de cambio de estatus registrado con éxito"}


@pytest.mark.asyncio
async def test_obtener_historial_obra():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/obras/historico/1001")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id_obra"] == 1001
        assert data[0]["estatus_nuevo"] == "Reservada"


@pytest.mark.asyncio
async def test_obtener_historial_obra_no_encontrada():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/obras/historico/9999")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_registrar_log_seguridad():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "login_usuario": "admin",
            "fecha_evento": datetime.now(timezone.utc).isoformat(),
            "evento_tipo": "LOGIN_EXITOSO",
            "ip_origen": "192.168.1.10",
            "detalles": "Ingreso al sistema",
            "usuario_id": 1,
        }
        response = await client.post("/seguridad/logs", json=payload)
        assert response.status_code == 201


@pytest.mark.asyncio
async def test_obtener_logs_seguridad():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/seguridad/logs?login_usuario=admin&desde=2023-01-01T00:00:00Z&hasta=2024-12-31T23:59:59Z"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["login_usuario"] == "admin"


@pytest.mark.asyncio
async def test_registrar_codigo_membresia():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "id_comprador": COMPRADOR_TEST,
            "fecha_registro": datetime.now(timezone.utc).isoformat(),
            "codigo_seguridad": "SECRET123",
            "correo_envio": "test@example.com",
            "estado": "EMITIDO",
        }
        response = await client.post("/membresias/codigos", json=payload)
        assert response.status_code == 201
        assert response.json()["mensaje"] == "Codigo de membresia insertado"


@pytest.mark.asyncio
async def test_obtener_codigos_membresia():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/membresias/codigos?id_comprador={COMPRADOR_TEST}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["datos"]) == 1
        assert data["datos"][0]["id_comprador"] == COMPRADOR_TEST


@pytest.mark.asyncio
async def test_obtener_reporte_facturacion():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/reportes/facturacion?anio=2025&mes=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["anio"] == 2025
        assert data[0]["mes"] == 1
        assert data[0]["id_comprador"] == 101


@pytest.mark.asyncio
async def test_obtener_reporte_membresias():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/reportes/membresias?anio=2025&mes=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["anio"] == 2025
        assert data[0]["mes"] == 1
        assert data[0]["codigo_membresia"] == "MEM-2025-A001"


@pytest.mark.asyncio
async def test_post_reporte_facturacion():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "anio": 2025,
            "mes": 1,
            "id_factura": 1001,
            "fecha_emision": datetime.now(timezone.utc).isoformat(),
            "id_comprador": 101,
            "monto_neto": 150.0,
            "iva_calculado": 24.0,
            "ganancia_museo": 45.0,
            "estado": "pagada",
        }
        response = await client.post("/reportes/facturacion", json=payload)
        assert response.status_code == 201
        assert response.json()["mensaje"] == "Reporte de facturación insertado correctamente"


@pytest.mark.asyncio
async def test_post_reporte_membresia():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "anio": 2025,
            "mes": 1,
            "id_membresia": 2001,
            "fecha_registro": datetime.now(timezone.utc).isoformat(),
            "id_comprador": 101,
            "codigo_membresia": "MEM-2025-A001",
            "monto_cobrado": 10.0,
            "estado": "activa",
        }
        response = await client.post("/reportes/membresias", json=payload)
        assert response.status_code == 201
        assert response.json()["mensaje"] == "Reporte de membresía insertado correctamente"


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code in (200, 503)
        data = response.json()
        assert "status" in data
        assert data["service"] == "Cassandra Audit Service"
