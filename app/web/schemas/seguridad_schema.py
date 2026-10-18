from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class EventoSeguridadEnum(str, Enum):
    LOGIN_EXITOSO = "LOGIN_EXITOSO"
    LOGIN_FALLIDO = "LOGIN_FALLIDO"


class SeguridadCreateDTO(BaseModel):
    login_usuario: str = Field(..., description="Username attempting access", examples=["jperez"])
    evento_tipo: str = Field(..., description="Security event type", examples=["LOGIN_EXITOSO"])
    usuario_id: int = Field(..., description="User ID in Core SQL responsible for the action", examples=[1])
    fecha_evento: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Event timestamp (UTC)"
    )
    ip_origen: Optional[str] = Field(default="127.0.0.1", description="Source IP address", examples=["192.168.1.10"])
    detalles: Optional[str] = Field(default=None, description="Additional event details", examples=["Successful login"])

    @field_validator("evento_tipo", mode="before")
    @classmethod
    def upper_evento(cls, v: str) -> str:
        return v.strip().upper()


class SeguridadResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    login_usuario: str
    fecha_evento: datetime
    evento_tipo: str
    ip_origen: Optional[str] = "127.0.0.1"
    detalles: Optional[str] = None
    usuario_id: int
