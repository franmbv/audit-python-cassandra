import asyncio
import base64
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID

from cassandra import DriverException
from cassandra.cluster import NoHostAvailable, Session
from cassandra.query import PreparedStatement

from app.config.database import conexion_cassandra
from app.schemas.membresias_schema import CodigoMembresiaSchema, EstadoCodigoMembresia

logger = logging.getLogger("cassandra")


class AuditRepositorio:
    def __init__(self):
        self._insert_prepared: Optional[PreparedStatement] = None
        self._query_prepared: Optional[PreparedStatement] = None

    async def _inicializar(self):
        if self._insert_prepared is not None and self._query_prepared is not None:
            return

        session = conexion_cassandra.session
        assert session is not None, "Cassandra session no inicializada. Ejecuta conexion_cassandra.conectar() primero."

        self._insert_prepared = await asyncio.to_thread(
            session.prepare,
            "INSERT INTO auditoria_codigos_membresia "
            "(id_comprador, fecha_registro, codigo_seguridad, correo_envio, estado) "
            "VALUES (?, ?, ?, ?, ?)"
        )
        self._query_prepared = await asyncio.to_thread(
            session.prepare,
            "SELECT id_comprador, fecha_registro, codigo_seguridad, correo_envio, estado "
            "FROM auditoria_codigos_membresia "
            "WHERE id_comprador = ?"
        )

    async def insertar_codigo(self, datos: CodigoMembresiaSchema) -> CodigoMembresiaSchema:
        await self._inicializar()
        session = conexion_cassandra.session
        assert session is not None, "Cassandra session no inicializada."
        assert self._insert_prepared is not None, "Prepared statement no inicializado."

        await asyncio.to_thread(
            session.execute,
            self._insert_prepared,
            (
                datos.id_comprador,
                datos.fecha_registro,
                datos.codigo_seguridad,
                str(datos.correo_envio),
                datos.estado.value if isinstance(datos.estado, EstadoCodigoMembresia) else str(datos.estado),
            ),
        )
        return datos

    async def obtener_codigos_por_comprador(
        self,
        id_comprador: UUID,
        page_size: int = 20,
        paging_state: Optional[str] = None,
    ) -> Tuple[List[CodigoMembresiaSchema], Optional[str]]:
        await self._inicializar()
        session = conexion_cassandra.session
        assert session is not None, "Cassandra session no inicializada."
        assert self._query_prepared is not None, "Prepared statement no inicializado."

        paging_state_bytes = base64.b64decode(paging_state) if paging_state else None
        consulta = self._query_prepared.bind((id_comprador,))
        consulta.fetch_size = page_size

        result = await asyncio.to_thread(
            session.execute,
            consulta,
            paging_state=paging_state_bytes,
        )

        registros: List[CodigoMembresiaSchema] = [
            CodigoMembresiaSchema(
                id_comprador=row.id_comprador,
                fecha_registro=row.fecha_registro,
                codigo_seguridad=row.codigo_seguridad,
                correo_envio=row.correo_envio,
                estado=row.estado,
            )
            for row in result
        ]

        siguiente_paging_state = None
        if getattr(result, "has_more_pages", False) and getattr(result, "paging_state", None):
            siguiente_paging_state = base64.b64encode(result.paging_state).decode("utf-8")

        return registros, siguiente_paging_state


class BaseCassandraRepository(ABC):
    """
    Clase base para los repositorios de Cassandra.
    Maneja la lógica centralizada de conexión, reintentos y preparación de sentencias.
    """
    def __init__(self):
        self._inicializado = False

    @abstractmethod
    async def _preparar_sentencias(self, session: Session) -> None:
        """
        Método abstracto donde las clases hijas deben preparar sus sentencias CQL.
        """
        pass

    async def _asegurar_inicializacion(self, max_reintentos: int = 3, espera_segundos: int = 2):
        """
        Garantiza que la sesión esté activa y las sentencias preparadas.
        Implementa lógica de reintentos para robustez.
        """
        if self._inicializado:
            return

        for intento in range(1, max_reintentos + 1):
            try:
                session = conexion_cassandra.session
                if session is None:
                    logger.warning(f"[Cassandra] Intento {intento}: Sesión nula, reconectando...")
                    conexion_cassandra.conectar()
                    session = conexion_cassandra.session

                if session:
                    await self._preparar_sentencias(session)
                    self._inicializado = True
                    logger.info(f"[Cassandra] {self.__class__.__name__} inicializado con éxito.")
                    return
                else:
                    raise DriverException("No se pudo obtener una sesión válida de Cassandra.")

            except (NoHostAvailable, DriverException) as e:
                logger.error(
                    "Intento %d de %d fallido para %s: %s",
                    intento, max_reintentos, self.__class__.__name__, e
                )
                if intento == max_reintentos:
                    raise RuntimeError(f"Error crítico: No se pudo inicializar el repositorio {self.__class__.__name__}.") from e
                await asyncio.sleep(espera_segundos)