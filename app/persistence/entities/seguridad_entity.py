from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SeguridadEntity(BaseModel):
    """Physical representation of records in table bitacora_seguridad."""
    model_config = ConfigDict(from_attributes=True)

    login_usuario: str
    fecha_evento: datetime
    accion: str
    ip_origen: Optional[str] = "127.0.0.1"
    detalles: Optional[str] = None
    usuario_id: int
