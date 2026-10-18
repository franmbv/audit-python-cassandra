from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from app.domain.models.membresia import CodigoMembresia


class MembresiaRepository(ABC):
    """Abstract interface defining persistence operations for membership codes."""

    @abstractmethod
    async def create_codigo(self, codigo: CodigoMembresia) -> CodigoMembresia:
        """Records a newly issued membership security code."""
        pass

    @abstractmethod
    async def get_codigos_by_comprador(
        self,
        id_comprador: int,
        page_size: int = 20,
        paging_state: Optional[str] = None,
    ) -> Tuple[List[CodigoMembresia], Optional[str]]:
        """Retrieves paginated membership codes issued to a buyer."""
        pass
