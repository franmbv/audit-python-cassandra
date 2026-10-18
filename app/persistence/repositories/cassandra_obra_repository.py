import asyncio
import logging
from typing import List, Optional
from cassandra import DriverException
from cassandra.cluster import Session
from cassandra.query import PreparedStatement

from app.domain.models.obra import ObraHistorial
from app.domain.repositories.obra_repository import ObraRepository
from app.domain.exceptions.domain_exceptions import DatabaseConnectionError
from app.persistence.config.database import db_cassandra
from app.persistence.mappers.obra_mapper import ObraMapper
from app.persistence.repositories.base_cassandra_repository import BaseCassandraRepository

logger = logging.getLogger("cassandra")


class CassandraObraRepository(BaseCassandraRepository, ObraRepository):
    """Cassandra persistence implementation for artwork audit history."""

    def __init__(self):
        super().__init__()
        self._insert_stmt: Optional[PreparedStatement] = None
        self._select_stmt: Optional[PreparedStatement] = None

    async def _preparar_sentencias(self, session: Session) -> None:
        self._insert_stmt = await asyncio.to_thread(
            session.prepare,
            "INSERT INTO historico_estatus_obras "
            "(id_obra, fecha_evento, estatus_anterior, estatus_nuevo, usuario_id, ip_origen) "
            "VALUES (?, ?, ?, ?, ?, ?)"
        )
        self._select_stmt = await asyncio.to_thread(
            session.prepare,
            "SELECT id_obra, fecha_evento, estatus_anterior, estatus_nuevo, usuario_id, ip_origen "
            "FROM historico_estatus_obras "
            "WHERE id_obra = ?"
        )

    async def create_historial(self, historial: ObraHistorial) -> None:
        await self._asegurar_inicializacion()
        session = db_cassandra.session
        assert session is not None
        assert self._insert_stmt is not None

        try:
            await asyncio.to_thread(
                session.execute,
                self._insert_stmt,
                (
                    historial.id_obra,
                    historial.fecha_evento,
                    historial.estatus_anterior,
                    historial.estatus_nuevo,
                    historial.usuario_id,
                    historial.ip_origen,
                ),
            )
        except DriverException as e:
            logger.error("[Cassandra] Error inserting artwork history %d: %s", historial.id_obra, e)
            raise DatabaseConnectionError(f"Database error while recording history: {e}") from e

    async def get_historial_by_obra(self, id_obra: int) -> List[ObraHistorial]:
        await self._asegurar_inicializacion()
        session = db_cassandra.session
        assert session is not None
        assert self._select_stmt is not None

        try:
            rows = await asyncio.to_thread(
                session.execute,
                self._select_stmt,
                (id_obra,),
            )
            return [ObraMapper.from_row(row) for row in rows]
        except DriverException as e:
            logger.error("[Cassandra] Error querying artwork history %d: %s", id_obra, e)
            raise DatabaseConnectionError(f"Database error while querying history: {e}") from e
