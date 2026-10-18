import asyncio
import base64
import logging
from typing import List, Optional, Tuple
from cassandra import DriverException
from cassandra.cluster import Session
from cassandra.query import PreparedStatement

from app.domain.models.membresia import CodigoMembresia
from app.domain.repositories.membresia_repository import MembresiaRepository
from app.domain.exceptions.domain_exceptions import DatabaseConnectionError
from app.persistence.config.database import db_cassandra
from app.persistence.mappers.membresia_mapper import MembresiaMapper
from app.persistence.repositories.base_cassandra_repository import BaseCassandraRepository

logger = logging.getLogger("cassandra")


class CassandraMembresiaRepository(BaseCassandraRepository, MembresiaRepository):
    """Cassandra persistence implementation for paginated membership security codes."""

    def __init__(self):
        super().__init__()
        self._insert_stmt: Optional[PreparedStatement] = None
        self._select_stmt: Optional[PreparedStatement] = None

    async def _preparar_sentencias(self, session: Session) -> None:
        self._insert_stmt = await asyncio.to_thread(
            session.prepare,
            "INSERT INTO auditoria_codigos_membresia "
            "(id_comprador, fecha_registro, codigo_seguridad, correo_envio, estado) "
            "VALUES (?, ?, ?, ?, ?)"
        )
        self._select_stmt = await asyncio.to_thread(
            session.prepare,
            "SELECT id_comprador, fecha_registro, codigo_seguridad, correo_envio, estado "
            "FROM auditoria_codigos_membresia "
            "WHERE id_comprador = ?"
        )

    async def create_codigo(self, codigo: CodigoMembresia) -> CodigoMembresia:
        await self._asegurar_inicializacion()
        session = db_cassandra.session
        assert session is not None
        assert self._insert_stmt is not None

        try:
            await asyncio.to_thread(
                session.execute,
                self._insert_stmt,
                (
                    codigo.id_comprador,
                    codigo.fecha_registro,
                    codigo.codigo_seguridad,
                    codigo.correo_envio,
                    codigo.estado,
                ),
            )
            return codigo
        except DriverException as e:
            logger.error("[Cassandra] Error inserting membership code: %s", e)
            raise DatabaseConnectionError(f"Database error while recording code: {e}") from e

    async def get_codigos_by_comprador(
        self,
        id_comprador: int,
        page_size: int = 20,
        paging_state: Optional[str] = None,
    ) -> Tuple[List[CodigoMembresia], Optional[str]]:
        await self._asegurar_inicializacion()
        session = db_cassandra.session
        assert session is not None
        assert self._select_stmt is not None

        paging_state_bytes = base64.b64decode(paging_state) if paging_state else None
        consulta = self._select_stmt.bind((id_comprador,))
        consulta.fetch_size = page_size

        try:
            result = await asyncio.to_thread(
                session.execute,
                consulta,
                paging_state=paging_state_bytes,
            )

            registros = [MembresiaMapper.from_row(row) for row in result]

            siguiente_paging_state = None
            if getattr(result, "has_more_pages", False) and getattr(result, "paging_state", None):
                siguiente_paging_state = base64.b64encode(result.paging_state).decode("utf-8")

            return registros, siguiente_paging_state
        except DriverException as e:
            logger.error("[Cassandra] Error querying membership codes for buyer %d: %s", id_comprador, e)
            raise DatabaseConnectionError(f"Database error while querying codes: {e}") from e
