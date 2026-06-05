from datetime import datetime, timezone
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class EstadoCodigoMembresia(str, Enum):
    EMITIDO = "EMITIDO"


class CodigoMembresiaSchema(BaseModel):
    id_comprador: UUID = Field(
        ...,
        description="Identificador unico del comprador",
        examples=["550e8400-e29b-41d4-a716-446655440001"],
    )

    codigo_seguridad: str = Field(
        ...,
        min_length=6,
        max_length=32,
        description="Codigo de seguridad emitido para la membresia",
        examples=["MK8X2Q9Z"],
    )

    correo_envio: EmailStr = Field(
        ...,
        description="Correo al que se envio el codigo de seguridad",
        examples=["comprador@correo.com"],
    )

    fecha_registro: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha y hora de registro del codigo en Cassandra",
    )

    estado: EstadoCodigoMembresia = Field(
        default=EstadoCodigoMembresia.EMITIDO,
        description="Estado funcional del codigo de membresia",
    )

    @field_validator("codigo_seguridad", mode="before")
    @classmethod
    def normalizar_codigo(cls, value: str) -> str:
        return value.strip().upper()

    model_config = {
        "json_schema_extra": {
            "example": {
                "id_comprador": "550e8400-e29b-41d4-a716-446655440001",
                "codigo_seguridad": "MK8X2Q9Z",
                "correo_envio": "comprador@correo.com",
                "fecha_registro": "2026-06-04T12:00:00Z",
                "estado": "EMITIDO",
            }
        }
    }


class RespuestaCodigoMembresiaSchema(CodigoMembresiaSchema):
    pass


class PaginaCodigoMembresiaSchema(BaseModel):
    datos: list[CodigoMembresiaSchema]
    paging_state: str | None = None