import asyncio
import logging
from abc import ABC, abstractmethod
from cassandra import DriverException
from cassandra.cluster import NoHostAvailable, Session

from app.domain.exceptions.domain_exceptions import DatabaseConnectionError
from app.persistence.config.database import db_cassandra

logger = logging.getLogger("cassandra")


class BaseCassandraRepository(ABC):
    """
    Base repository for Apache Cassandra / Astra DB implementations.
    Manages lazy, thread-safe CQL prepared statement lifecycle and retries.
    """

    def __init__(self):
        self._inicializado = False
        self._lock = asyncio.Lock()

    @abstractmethod
    async def _preparar_sentencias(self, session: Session) -> None:
        """Abstract method implemented by subclasses to prepare their CQL statements."""
        pass

    async def _asegurar_inicializacion(self, max_reintentos: int = 3, espera_segundos: int = 2) -> None:
        """Asynchronously and thread-safely ensures the session is active and statements are prepared."""
        if self._inicializado:
            return

        async with self._lock:
            if self._inicializado:
                return

            for intento in range(1, max_reintentos + 1):
                try:
                    session = db_cassandra.session
                    if session is None or session.is_shutdown:
                        logger.warning(
                            "[Cassandra] Attempt %d/%d: Session not ready, connecting...",
                            intento, max_reintentos
                        )
                        session = await asyncio.to_thread(db_cassandra.conectar)

                    if session and not session.is_shutdown:
                        await self._preparar_sentencias(session)
                        self._inicializado = True
                        logger.info("[Cassandra] Repository %s successfully prepared.", self.__class__.__name__)
                        return

                except (NoHostAvailable, DriverException, Exception) as e:
                    logger.error(
                        "[Cassandra] Failed attempt %d/%d for %s: %s",
                        intento, max_reintentos, self.__class__.__name__, e
                    )
                    if intento == max_reintentos:
                        raise DatabaseConnectionError(
                            f"Could not connect or initialize repository {self.__class__.__name__}: {e}"
                        ) from e
                    await asyncio.sleep(espera_segundos)
