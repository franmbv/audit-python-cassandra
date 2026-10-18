from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, Query, status

from app.domain.models.seguridad import SeguridadLog
from app.domain.services.seguridad_service import SeguridadService
from app.web.dependencies import get_seguridad_service
from app.web.schemas.seguridad_schema import SeguridadCreateDTO, SeguridadResponseDTO

router = APIRouter(prefix="/seguridad", tags=["Security"])


@router.post(
    "/logs",
    status_code=status.HTTP_201_CREATED,
    summary="Record an event in the security audit log",
)
async def crear_log(
    dto: SeguridadCreateDTO,
    service: SeguridadService = Depends(get_seguridad_service),
):
    model = SeguridadLog(
        login_usuario=dto.login_usuario,
        fecha_evento=dto.fecha_evento,
        accion=dto.evento_tipo,
        ip_origen=dto.ip_origen,
        detalles=dto.detalles,
        usuario_id=dto.usuario_id,
    )
    await service.registrar_log(model)
    return {"mensaje": "Log de seguridad insertado", "datos": dto}


@router.get(
    "/logs",
    response_model=List[SeguridadResponseDTO],
    summary="Query security audit events by username and date range",
)
async def consultar_logs(
    login_usuario: str = Query(..., description="Username to audit"),
    desde: datetime = Query(..., description="Range start timestamp (ISO 8601)"),
    hasta: datetime = Query(..., description="Range end timestamp (ISO 8601)"),
    service: SeguridadService = Depends(get_seguridad_service),
):
    logs = await service.obtener_logs_usuario(login_usuario, desde, hasta)
    return [
        SeguridadResponseDTO(
            login_usuario=log.login_usuario,
            fecha_evento=log.fecha_evento,
            evento_tipo=log.accion,
            ip_origen=log.ip_origen,
            detalles=log.detalles,
            usuario_id=log.usuario_id,
        )
        for log in logs
    ]
