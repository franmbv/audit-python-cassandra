from typing import List
from app.domain.models.reporte import ReporteFacturacion, ReporteMembresia
from app.domain.repositories.reporte_repository import ReporteRepository


class ReporteService:
    """Domain service managing periodic billing and membership analytics aggregation."""

    def __init__(self, repo: ReporteRepository):
        self.repo = repo

    async def registrar_factura(self, reporte: ReporteFacturacion) -> ReporteFacturacion:
        await self.repo.create_factura(reporte)
        return reporte

    async def obtener_reporte_facturacion(self, anio: int, mes: int) -> List[ReporteFacturacion]:
        return await self.repo.get_reporte_facturacion(anio, mes)

    async def registrar_membresia(self, reporte: ReporteMembresia) -> ReporteMembresia:
        await self.repo.create_membresia(reporte)
        return reporte

    async def obtener_reporte_membresias(self, anio: int, mes: int) -> List[ReporteMembresia]:
        return await self.repo.get_reporte_membresias(anio, mes)
