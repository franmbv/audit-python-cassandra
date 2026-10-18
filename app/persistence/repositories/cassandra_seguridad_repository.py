import asyncio
import logging
from datetime import datetime
from typing import List, Optional
from cassandra import DriverException
from cassandra.cluster import Session
from cassandra.query import PreparedStatement

from app.domain.models.seguridad import SeguridadLog
from app.domain.repositories.seguridad_repository import SeguridadRepository
from app.domain.exceptions.domain_exceptions import DatabaseConnectionError
from app.persistence.config.database import db_cassandra
from app.persistence.mappers.seguridad_mapper import SeguridadMapper
from app.persistence.repositories.base_cassandra_repository import BaseCassandraRepository

logger = logging.getLogger("cassandra")


class CassandraSeguridadRepository(BaseCassandraRepository, SeguridadRepository):
    """Cassandra persistence implementation for security audit logs."""

    def __init__(self):
        super().__init__()
        self._insert_stmt: Optional[PreparedStatement] = None
        self._select_stmt: Optional[PreparedStatement] = None

    async def _preparar_sentencias(self, session: Session) -> None:
        self._insert_stmt = await asyncio.to_thread(
            session.prepare,
            "INSERT INTO bitacora_seguridad "
            "(login_usuario, fecha_evento, accion, ip_origen, detalles, usuario_id) "
            "VALUES (?, ?, ?, ?, ?, ?)"
        )
        self._select_stmt = await asyncio.to_thread(
            session.prepare,
            "SELECT login_usuario, fecha_evento, accion, ip_origen, detalles, usuario_id "
            "FROM bitacora_seguridad "
            "WHERE login_usuario = ? AND fecha_evento >= ? AND fecha_evento <= ? "
            "ORDER BY fecha_evento ASC"
        )

    async def create_log(self, log: SeguridadLog) -> None:
        await self._asegurar_inicializacion()
        session = db_cassandra.session
        assert session is not None
        assert self._insert_stmt is not None

        try:
            await asyncio.to_thread(
                session.execute,
                self._insert_stmt,
                (
                    log.login_usuario,
                    log.fecha_evento,
                    log.accion,
                    log.ip_origen,
                    log.detalles,
                    log.usuario_id,
                ),
            )
        except DriverException as e:
            logger.error("[Cassandra] Error inserting security log: %s", e)
            raise DatabaseConnectionError(f"Database error while recording security log: {e}") from e

    async def get_logs_by_user(
        self, login_usuario: str, desde: datetime, hasta: datetime
    ) -> List[SeguridadLog]:
        await self._asegurar_inicializacion()
        session = db_cassandra.session
        assert session is not None
        assert self._select_stmt is not None

        try:
            rows = await asyncio.to_thread(
                session.execute,
                self._select_stmt,
                (login_usuario, desde, hasta),
            )
            return [SeguridadMapper.from_row(row) for row in rows]
        except DriverException as e:
            logger.error("[Cassandra] Error querying security logs for %s: %s", login_usuario, e)
            raise DatabaseConnectionError(f"Database error while querying security logs: {e}") from e
