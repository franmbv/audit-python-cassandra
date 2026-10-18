from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ObraEntity(BaseModel):
    """Physical representation of records in table historico_estatus_obras."""
    model_config = ConfigDict(from_attributes=True)

    id_obra: int
    fecha_evento: datetime
    estatus_anterior: str
    estatus_nuevo: str
    usuario_id: int
    ip_origen: Optional[str] = "127.0.0.1"
