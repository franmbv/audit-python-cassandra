from typing import List, Optional, Tuple
from app.domain.models.membresia import CodigoMembresia
from app.domain.repositories.membresia_repository import MembresiaRepository


class MembresiaService:
    """Domain service managing membership security code issuance and auditing."""

    def __init__(self, repo: MembresiaRepository):
        self.repo = repo

    async def registrar_codigo(self, codigo: CodigoMembresia) -> CodigoMembresia:
        return await self.repo.create_codigo(codigo)

    async def obtener_codigos_comprador(
        self,
        id_comprador: int,
        page_size: int = 20,
        paging_state: Optional[str] = None,
    ) -> Tuple[List[CodigoMembresia], Optional[str]]:
        return await self.repo.get_codigos_by_comprador(
            id_comprador=id_comprador,
            page_size=page_size,
            paging_state=paging_state,
        )
