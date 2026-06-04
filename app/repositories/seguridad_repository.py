import asyncio
import logging
from datetime import datetime
from typing import List, Optional
from cassandra.query import PreparedStatement
from app.config.database import conexion_cassandra
from app.schemas.seguridad_schema import SeguridadSchema

logger = logging.getLogger("cassandra")


class SeguridadRepositorio:
    def __init__(self):
        self._insert_prepared: Optional[PreparedStatement] = None
        self._query_por_usuario: Optional[PreparedStatement] = None

    async def _inicializar(self):
        if self._insert_prepared is not None:
            return
        session = conexion_cassandra.session
        assert session is not None, "Cassandra session no inicializada. Ejecuta conexion_cassandra.conectar() primero."
        self._insert_prepared = await asyncio.to_thread(
            session.prepare,
            "INSERT INTO bitacora_seguridad "
            "(login_usuario, fecha_evento, accion, ip_origen, detalles, usuario_id) "
            "VALUES (?, ?, ?, ?, ?, ?)"
        )

    async def insertar_log(self, datos: SeguridadSchema) -> None:
        await self._inicializar()
        session = conexion_cassandra.session
        assert session is not None, "Cassandra session no inicializada."
        assert self._insert_prepared is not None, "Prepared statement no inicializado. Llama a _inicializar() primero."
        try:
            await asyncio.to_thread(
                session.execute,
                self._insert_prepared,
                (
                    datos.login_usuario,
                    datos.fecha_evento,
                    datos.evento_tipo,
                    datos.ip_origen,
                    datos.detalles,
                    datos.usuario_id,
                ),
            )
            logger.info(
                "Log de seguridad insertado: login=%s, evento=%s, ip=%s",
                datos.login_usuario,
                datos.evento_tipo,
                datos.ip_origen,
            )
        except Exception as e:
            logger.error(
                "Error al insertar log de seguridad: login=%s, evento=%s, error=%s",
                datos.login_usuario,
                datos.evento_tipo,
                e,
            )
            raise
