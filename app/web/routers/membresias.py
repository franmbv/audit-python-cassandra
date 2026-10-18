from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.domain.models.membresia import CodigoMembresia
from app.domain.services.membresia_service import MembresiaService
from app.web.dependencies import get_membresia_service
from app.web.schemas.membresia_schema import (
    CodigoMembresiaCreateDTO,
    CodigoMembresiaResponseDTO,
    PaginaCodigoMembresiaDTO,
)

router = APIRouter(prefix="/membresias", tags=["Memberships"])


@router.post(
    "/codigos",
    status_code=status.HTTP_201_CREATED,
    summary="Record an issued membership code",
)
async def crear_codigo(
    dto: CodigoMembresiaCreateDTO,
    service: MembresiaService = Depends(get_membresia_service),
):
    model = CodigoMembresia(
        id_comprador=dto.id_comprador,
        fecha_registro=dto.fecha_registro,
        codigo_seguridad=dto.codigo_seguridad,
        correo_envio=str(dto.correo_envio),
        estado=dto.estado,
    )
    registro = await service.registrar_codigo(model)
    return {
        "mensaje": "Codigo de membresia insertado",
        "datos": CodigoMembresiaResponseDTO(
            id_comprador=registro.id_comprador,
            fecha_registro=registro.fecha_registro,
            codigo_seguridad=registro.codigo_seguridad,
            correo_envio=registro.correo_envio,
            estado=registro.estado,
        ),
    }


@router.get(
    "/codigos",
    response_model=PaginaCodigoMembresiaDTO,
    summary="Retrieve paginated membership codes by buyer",
)
async def consultar_codigos(
    id_comprador: int = Query(..., description="Unique buyer identifier"),
    page_size: int = Query(20, ge=1, le=100, description="Page size limit"),
    paging_state: Optional[str] = Query(None, description="Base64 paging token returned from previous page"),
    service: MembresiaService = Depends(get_membresia_service),
):
    registros, siguiente_paging_state = await service.obtener_codigos_comprador(
        id_comprador=id_comprador,
        page_size=page_size,
        paging_state=paging_state,
    )
    dtos = [
        CodigoMembresiaResponseDTO(
            id_comprador=r.id_comprador,
            fecha_registro=r.fecha_registro,
            codigo_seguridad=r.codigo_seguridad,
            correo_envio=r.correo_envio,
            estado=r.estado,
        )
        for r in registros
    ]
    return PaginaCodigoMembresiaDTO(datos=dtos, paging_state=siguiente_paging_state)
