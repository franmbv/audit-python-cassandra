from typing import List
from fastapi import APIRouter, Depends, Path, status

from app.domain.models.obra import ObraHistorial
from app.domain.services.obra_service import ObraService
from app.web.dependencies import get_obra_service
from app.web.schemas.obra_schema import ObraCreateDTO, ObraResponseDTO

router = APIRouter(prefix="/obras", tags=["Artworks"])


@router.post(
    "/historico",
    status_code=status.HTTP_201_CREATED,
    summary="Record an artwork status change audit event",
)
async def registrar_evento(
    dto: ObraCreateDTO,
    service: ObraService = Depends(get_obra_service),
):
    model = ObraHistorial(
        id_obra=dto.id_obra,
        fecha_evento=dto.fecha_evento,
        estatus_anterior=dto.estatus_anterior,
        estatus_nuevo=dto.estatus_nuevo,
        usuario_id=dto.usuario_id,
        ip_origen=dto.ip_origen,
    )
    await service.registrar_cambio_estatus(model)
    return {"mensaje": "Historial de cambio de estatus registrado con éxito"}


@router.get(
    "/historico/{id_obra}",
    response_model=List[ObraResponseDTO],
    summary="Retrieve chronological status changes for an artwork",
)
async def obtener_historial_obra(
    id_obra: int = Path(..., description="Numeric identifier of the artwork", example=1001),
    service: ObraService = Depends(get_obra_service),
):
    resultados = await service.obtener_historial_obra(id_obra)
    return [
        ObraResponseDTO(
            id_obra=r.id_obra,
            fecha_evento=r.fecha_evento,
            estatus_anterior=r.estatus_anterior,
            estatus_nuevo=r.estatus_nuevo,
            usuario_id=r.usuario_id,
            ip_origen=r.ip_origen,
        )
        for r in resultados
    ]
