from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class ObraHistorial(BaseModel):
    """Pure domain entity for artwork status change audit records."""
    id_obra: int
    fecha_evento: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    estatus_anterior: str
    estatus_nuevo: str
    usuario_id: int
    ip_origen: Optional[str] = "127.0.0.1"
