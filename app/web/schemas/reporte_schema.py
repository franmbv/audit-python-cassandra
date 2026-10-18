from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class ReporteFacturacionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    anio: int = Field(..., ge=2020, le=2100, description="Fiscal year")
    mes: int = Field(..., ge=1, le=12, description="Fiscal month (1-12)")
    id_factura: int
    fecha_emision: datetime
    id_comprador: int
    monto_neto: Decimal
    iva_calculado: Decimal
    ganancia_museo: Decimal
    estado: str


class ReporteMembresiaDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    anio: int = Field(..., ge=2020, le=2100, description="Fiscal year")
    mes: int = Field(..., ge=1, le=12, description="Fiscal month (1-12)")
    id_membresia: int
    fecha_registro: datetime
    id_comprador: int
    codigo_membresia: str
    monto_cobrado: Decimal
    estado: str
