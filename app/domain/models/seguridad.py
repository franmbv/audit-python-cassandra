from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class SeguridadLog(BaseModel):
    """Pure domain entity for security audit events."""
    login_usuario: str
    fecha_evento: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    accion: str
    ip_origen: Optional[str] = "127.0.0.1"
    detalles: Optional[str] = None
    usuario_id: int
