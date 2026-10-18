from typing import List
from fastapi import APIRouter, Depends, Query, status

from app.domain.models.reporte import ReporteFacturacion, ReporteMembresia
from app.domain.services.reporte_service import ReporteService
from app.web.dependencies import get_reporte_service
from app.web.schemas.reporte_schema import ReporteFacturacionDTO, ReporteMembresiaDTO

router = APIRouter(prefix="/reportes", tags=["Reports"])


@router.get(
    "/facturacion",
    response_model=List[ReporteFacturacionDTO],
    summary="Retrieve billing audit report for a fiscal year and month",
)
async def get_reporte_facturacion(
    anio: int = Query(..., ge=2020, le=2100, description="Fiscal year"),
    mes: int = Query(..., ge=1, le=12, description="Fiscal month (1-12)"),
    service: ReporteService = Depends(get_reporte_service),
):
    resultados = await service.obtener_reporte_facturacion(anio, mes)
    return [ReporteFacturacionDTO.model_validate(r) for r in resultados]


@router.post(
    "/facturacion",
    status_code=status.HTTP_201_CREATED,
    summary="Record an invoice transaction in the analytical audit report",
)
async def post_reporte_facturacion(
    dto: ReporteFacturacionDTO,
    service: ReporteService = Depends(get_reporte_service),
):
    model = ReporteFacturacion(
        anio=dto.anio,
        mes=dto.mes,
        id_factura=dto.id_factura,
        fecha_emision=dto.fecha_emision,
        id_comprador=dto.id_comprador,
        monto_neto=dto.monto_neto,
        iva_calculado=dto.iva_calculado,
        ganancia_museo=dto.ganancia_museo,
        estado=dto.estado,
    )
    await service.registrar_factura(model)
    return {"mensaje": "Reporte de facturación insertado correctamente"}


@router.get(
    "/membresias",
    response_model=List[ReporteMembresiaDTO],
    summary="Retrieve membership audit report for a fiscal year and month",
)
async def get_reporte_membresias(
    anio: int = Query(..., ge=2020, le=2100, description="Fiscal year"),
    mes: int = Query(..., ge=1, le=12, description="Fiscal month (1-12)"),
    service: ReporteService = Depends(get_reporte_service),
):
    resultados = await service.obtener_reporte_membresias(anio, mes)
    return [ReporteMembresiaDTO.model_validate(r) for r in resultados]


@router.post(
    "/membresias",
    status_code=status.HTTP_201_CREATED,
    summary="Record a membership transaction in the analytical audit report",
)
async def post_reporte_membresia(
    dto: ReporteMembresiaDTO,
    service: ReporteService = Depends(get_reporte_service),
):
    model = ReporteMembresia(
        anio=dto.anio,
        mes=dto.mes,
        id_membresia=dto.id_membresia,
        fecha_registro=dto.fecha_registro,
        id_comprador=dto.id_comprador,
        codigo_membresia=dto.codigo_membresia,
        monto_cobrado=dto.monto_cobrado,
        estado=dto.estado,
    )
    await service.registrar_membresia(model)
    return {"mensaje": "Reporte de membresía insertado correctamente"}
