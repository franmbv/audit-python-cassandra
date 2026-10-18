import asyncio
import logging
from typing import List, Optional
from cassandra import DriverException
from cassandra.cluster import Session
from cassandra.query import PreparedStatement

from app.domain.models.reporte import ReporteFacturacion, ReporteMembresia
from app.domain.repositories.reporte_repository import ReporteRepository
from app.domain.exceptions.domain_exceptions import DatabaseConnectionError
from app.persistence.config.database import db_cassandra
from app.persistence.mappers.reporte_mapper import ReporteFacturacionMapper, ReporteMembresiaMapper
from app.persistence.repositories.base_cassandra_repository import BaseCassandraRepository

logger = logging.getLogger("cassandra")


class CassandraReporteRepository(BaseCassandraRepository, ReporteRepository):
    """Cassandra persistence implementation for periodic billing and membership reports."""

    def __init__(self):
        super().__init__()
        self._insert_factura_stmt: Optional[PreparedStatement] = None
        self._select_factura_stmt: Optional[PreparedStatement] = None
        self._insert_membresia_stmt: Optional[PreparedStatement] = None
        self._select_membresia_stmt: Optional[PreparedStatement] = None

    async def _preparar_sentencias(self, session: Session) -> None:
        self._insert_factura_stmt = await asyncio.to_thread(
            session.prepare,
            "INSERT INTO reporte_facturacion_periodo "
            "(anio, mes, id_factura, fecha_emision, id_comprador, monto_neto, iva_calculado, ganancia_museo, estado) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        self._select_factura_stmt = await asyncio.to_thread(
            session.prepare,
            "SELECT anio, mes, id_factura, fecha_emision, id_comprador, monto_neto, iva_calculado, ganancia_museo, estado "
            "FROM reporte_facturacion_periodo "
            "WHERE anio = ? AND mes = ?"
        )
        self._insert_membresia_stmt = await asyncio.to_thread(
            session.prepare,
            "INSERT INTO reporte_membresias_periodo "
            "(anio, mes, id_membresia, fecha_registro, id_comprador, codigo_membresia, monto_cobrado, estado) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        )
        self._select_membresia_stmt = await asyncio.to_thread(
            session.prepare,
            "SELECT anio, mes, id_membresia, fecha_registro, id_comprador, codigo_membresia, monto_cobrado, estado "
            "FROM reporte_membresias_periodo "
            "WHERE anio = ? AND mes = ?"
        )

    async def create_factura(self, reporte: ReporteFacturacion) -> None:
        await self._asegurar_inicializacion()
        session = db_cassandra.session
        assert session is not None
        assert self._insert_factura_stmt is not None

        try:
            await asyncio.to_thread(
                session.execute,
                self._insert_factura_stmt,
                (
                    reporte.anio,
                    reporte.mes,
                    reporte.id_factura,
                    reporte.fecha_emision,
                    reporte.id_comprador,
                    reporte.monto_neto,
                    reporte.iva_calculado,
                    reporte.ganancia_museo,
                    reporte.estado,
                ),
            )
        except DriverException as e:
            logger.error("[Cassandra] Error inserting invoice report %d: %s", reporte.id_factura, e)
            raise DatabaseConnectionError(f"Database error while recording invoice: {e}") from e

    async def get_reporte_facturacion(self, anio: int, mes: int) -> List[ReporteFacturacion]:
        await self._asegurar_inicializacion()
        session = db_cassandra.session
        assert session is not None
        assert self._select_factura_stmt is not None

        try:
            rows = await asyncio.to_thread(
                session.execute,
                self._select_factura_stmt,
                (anio, mes),
            )
            return [ReporteFacturacionMapper.from_row(row) for row in rows]
        except DriverException as e:
            logger.error("[Cassandra] Error querying billing report %d-%d: %s", anio, mes, e)
            raise DatabaseConnectionError(f"Database error while querying billing: {e}") from e

    async def create_membresia(self, reporte: ReporteMembresia) -> None:
        await self._asegurar_inicializacion()
        session = db_cassandra.session
        assert session is not None
        assert self._insert_membresia_stmt is not None

        try:
            await asyncio.to_thread(
                session.execute,
                self._insert_membresia_stmt,
                (
                    reporte.anio,
                    reporte.mes,
                    reporte.id_membresia,
                    reporte.fecha_registro,
                    reporte.id_comprador,
                    reporte.codigo_membresia,
                    reporte.monto_cobrado,
                    reporte.estado,
                ),
            )
        except DriverException as e:
            logger.error("[Cassandra] Error inserting membership report %d: %s", reporte.id_membresia, e)
            raise DatabaseConnectionError(f"Database error while recording membership: {e}") from e

    async def get_reporte_membresias(self, anio: int, mes: int) -> List[ReporteMembresia]:
        await self._asegurar_inicializacion()
        session = db_cassandra.session
        assert session is not None
        assert self._select_membresia_stmt is not None

        try:
            rows = await asyncio.to_thread(
                session.execute,
                self._select_membresia_stmt,
                (anio, mes),
            )
            return [ReporteMembresiaMapper.from_row(row) for row in rows]
        except DriverException as e:
            logger.error("[Cassandra] Error querying membership report %d-%d: %s", anio, mes, e)
            raise DatabaseConnectionError(f"Database error while querying memberships: {e}") from e
