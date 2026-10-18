from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class ReporteFacturacionEntity(BaseModel):
    """Physical representation of records in table reporte_facturacion_periodo."""
    model_config = ConfigDict(from_attributes=True)

    anio: int
    mes: int
    id_factura: int
    fecha_emision: datetime
    id_comprador: int
    monto_neto: Decimal
    iva_calculado: Decimal
    ganancia_museo: Decimal
    estado: str


class ReporteMembresiaEntity(BaseModel):
    """Physical representation of records in table reporte_membresias_periodo."""
    model_config = ConfigDict(from_attributes=True)

    anio: int
    mes: int
    id_membresia: int
    fecha_registro: datetime
    id_comprador: int
    codigo_membresia: str
    monto_cobrado: Decimal
    estado: str
