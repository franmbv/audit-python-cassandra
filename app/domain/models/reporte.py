from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class ReporteFacturacion(BaseModel):
    """Pure domain entity for periodic billing audit reports."""
    anio: int
    mes: int
    id_factura: int
    fecha_emision: datetime
    id_comprador: int
    monto_neto: Decimal
    iva_calculado: Decimal
    ganancia_museo: Decimal
    estado: str


class ReporteMembresia(BaseModel):
    """Pure domain entity for periodic membership audit reports."""
    anio: int
    mes: int
    id_membresia: int
    fecha_registro: datetime
    id_comprador: int
    codigo_membresia: str
    monto_cobrado: Decimal
    estado: str
