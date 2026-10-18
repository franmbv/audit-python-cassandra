from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ObraCreateDTO(BaseModel):
    id_obra: int = Field(..., description="Numeric identifier of the artwork", examples=[1001])
    estatus_anterior: str = Field(..., description="Previous artwork status", examples=["Disponible"])
    estatus_nuevo: str = Field(..., description="New artwork status", examples=["Reservada"])
    usuario_id: int = Field(..., description="User ID in Core SQL responsible for the action", examples=[1])
    fecha_evento: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of the status change (UTC)"
    )
    ip_origen: Optional[str] = Field(default="127.0.0.1", description="Source IP address", examples=["192.168.1.10"])


class ObraResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_obra: int
    fecha_evento: datetime
    estatus_anterior: str
    estatus_nuevo: str
    usuario_id: int
    ip_origen: Optional[str] = "127.0.0.1"
