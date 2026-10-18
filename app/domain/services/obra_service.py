from typing import List
from app.domain.models.obra import ObraHistorial
from app.domain.repositories.obra_repository import ObraRepository
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class ObraService:
    """Domain service managing artwork audit history."""

    def __init__(self, repo: ObraRepository):
        self.repo = repo

    async def registrar_cambio_estatus(self, historial: ObraHistorial) -> ObraHistorial:
        await self.repo.create_historial(historial)
        return historial

    async def obtener_historial_obra(self, id_obra: int) -> List[ObraHistorial]:
        historial = await self.repo.get_historial_by_obra(id_obra)
        if not historial:
            raise EntityNotFoundError(f"No audit records found for artwork ID {id_obra}")
        return historial
