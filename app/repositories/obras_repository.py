import asyncio
import logging
from typing import List, Optional
from cassandra import DriverException
from cassandra.cluster import NoHostAvailable
from cassandra.query import PreparedStatement

from app.config.database import conexion_cassandra
from app.schemas.obras_schema import ObrasSchema

logger = logging.getLogger("cassandra")


class ObrasRepositorio:
    def __init__(self):
        self._insert_prepared: Optional[PreparedStatement] = None
        self._query_por_obra: Optional[PreparedStatement] = None

    async def _inicializar(self, max_reintentos: int = 3, espera_segundos: int = 2):
        """
        Prepara las sentencias de Cassandra de forma segura.
        Incluye reintentos de conexión en caso de fallas transitorias.
        """
        if self._insert_prepared is not None and self._query_por_obra is not None:
            return

        for intento in range(1, max_reintentos + 1):
            try:
                session = conexion_cassandra.session
                if session is None:
                    logger.warning("[Cassandra] La sesión es nula, intentando reconectar...")
                    conexion_cassandra.conectar()
                    session = conexion_cassandra.session
                    assert session is not None, "La sesión no pudo ser inicializada."

                # Preparación de sentencias
                self._insert_prepared = await asyncio.to_thread(
                    session.prepare,
                    "INSERT INTO historico_estatus_obras "
                    "(id_obra, fecha_evento, estatus_anterior, estatus_nuevo, usuario_id, ip_origen) "
                    "VALUES (?, ?, ?, ?, ?, ?)"
                )

                self._query_por_obra = await asyncio.to_thread(
                    session.prepare,
                    "SELECT id_obra, fecha_evento, estatus_anterior, estatus_nuevo, usuario_id, ip_origen "
                    "FROM historico_estatus_obras "
                    "WHERE id_obra = ?"
                )
                logger.info("[Cassandra] Sentencias preparadas con éxito para Obras.")
                return

            except (NoHostAvailable, DriverException) as e:
                logger.error(
                    "Intento %d de %d fallido al preparar sentencias de Cassandra: %s",
                    intento, max_reintentos, e
                )
                if intento == max_reintentos:
                    raise RuntimeError("No se pudo conectar o preparar las consultas en Cassandra.") from e
                await asyncio.sleep(espera_segundos)

    async def registrar_cambio_estatus(self, datos: ObrasSchema) -> None:
        """
        Inserta un evento de auditoría de cambio de estado en Cassandra.
        """
        await self._inicializar()
        session = conexion_cassandra.session
        assert session is not None, "Sesión de Cassandra no disponible."
        assert self._insert_prepared is not None, "Sentencia preparada de inserción no inicializada."

        try:
            await asyncio.to_thread(
                session.execute,
                self._insert_prepared,
                (
                    datos.id_obra,
                    datos.fecha_evento,
                    datos.estatus_anterior,
                    datos.estatus_nuevo,
                    datos.usuario_id,
                    datos.ip_origen
                )
            )
            logger.info(
                "Historial de obra registrado: id_obra=%d, nuevo_estatus=%s",
                datos.id_obra, datos.estatus_nuevo
            )
        except DriverException as e:
            logger.error("Error del driver de Cassandra al insertar historial de obra: %s", e)
            raise RuntimeError("Fallo en la base de datos de auditoría al insertar registro.") from e

    async def obtener_historial(self, id_obra: int) -> List[ObrasSchema]:
        """
        Retorna el histórico de cambios de estado para una obra específica.
        """
        await self._inicializar()
        session = conexion_cassandra.session
        assert session is not None, "Sesión de Cassandra no disponible."
        assert self._query_por_obra is not None, "Sentencia preparada de selección no inicializada."

        try:
            rows = await asyncio.to_thread(
                session.execute,
                self._query_por_obra,
                (id_obra,)
            )

            resultados: List[ObrasSchema] = [
                ObrasSchema(
                    id_obra=row.id_obra,
                    fecha_evento=row.fecha_evento,
                    estatus_anterior=row.estatus_anterior,
                    estatus_nuevo=row.estatus_nuevo,
                    usuario_id=row.usuario_id,
                    ip_origen=row.ip_origen
                )
                for row in rows
            ]
            logger.info("Consulta exitosa: id_obra=%d, total_registros=%d", id_obra, len(resultados))
            return resultados

        except DriverException as e:
            logger.error("Error del driver de Cassandra al consultar historial de obra %d: %s", id_obra, e)
            raise RuntimeError("Fallo en la base de datos de auditoría al recuperar historial.") from e