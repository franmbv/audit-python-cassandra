from abc import ABC, abstractmethod
from typing import List
from app.domain.models.obra import ObraHistorial


class ObraRepository(ABC):
    """Abstract interface defining persistence operations for artwork history."""

    @abstractmethod
    async def create_historial(self, historial: ObraHistorial) -> None:
        """Records a new artwork status change event."""
        pass

    @abstractmethod
    async def get_historial_by_obra(self, id_obra: int) -> List[ObraHistorial]:
        """Retrieves chronological status changes for a specific artwork."""
        pass
