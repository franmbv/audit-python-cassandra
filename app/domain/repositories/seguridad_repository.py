from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from app.domain.models.seguridad import SeguridadLog


class SeguridadRepository(ABC):
    """Abstract interface defining persistence operations for security audit logs."""

    @abstractmethod
    async def create_log(self, log: SeguridadLog) -> None:
        """Inserts a new record into the security audit log."""
        pass

    @abstractmethod
    async def get_logs_by_user(
        self, login_usuario: str, desde: datetime, hasta: datetime
    ) -> List[SeguridadLog]:
        """Queries security events for a user within a timestamp range."""
        pass
