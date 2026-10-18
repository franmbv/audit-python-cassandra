from datetime import datetime
from typing import List
from app.domain.models.seguridad import SeguridadLog
from app.domain.repositories.seguridad_repository import SeguridadRepository
from app.domain.exceptions.domain_exceptions import BusinessRuleConflictError


class SeguridadService:
    """Domain service managing security and access audit logs."""

    def __init__(self, repo: SeguridadRepository):
        self.repo = repo

    async def registrar_log(self, log: SeguridadLog) -> SeguridadLog:
        await self.repo.create_log(log)
        return log

    async def obtener_logs_usuario(
        self, login_usuario: str, desde: datetime, hasta: datetime
    ) -> List[SeguridadLog]:
        if desde > hasta:
            raise BusinessRuleConflictError("The 'desde' timestamp cannot be after 'hasta'.")
        return await self.repo.get_logs_by_user(login_usuario, desde, hasta)
