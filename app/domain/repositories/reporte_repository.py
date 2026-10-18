from abc import ABC, abstractmethod
from typing import List
from app.domain.models.reporte import ReporteFacturacion, ReporteMembresia


class ReporteRepository(ABC):
    """Abstract interface defining persistence operations for analytical periodic reports."""

    @abstractmethod
    async def create_factura(self, reporte: ReporteFacturacion) -> None:
        """Inserts an audit record into the periodic billing report."""
        pass

    @abstractmethod
    async def get_reporte_facturacion(self, anio: int, mes: int) -> List[ReporteFacturacion]:
        """Retrieves billing transactions for a fiscal period (year/month)."""
        pass

    @abstractmethod
    async def create_membresia(self, reporte: ReporteMembresia) -> None:
        """Inserts an audit record into the periodic membership report."""
        pass

    @abstractmethod
    async def get_reporte_membresias(self, anio: int, mes: int) -> List[ReporteMembresia]:
        """Retrieves membership transactions for a fiscal period (year/month)."""
        pass
