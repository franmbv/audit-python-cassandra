from datetime import datetime, timezone
from pydantic import BaseModel, Field


class CodigoMembresia(BaseModel):
    """Pure domain entity for an issued membership code."""
    id_comprador: int
    fecha_registro: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    codigo_seguridad: str
    correo_envio: str
    estado: str = "EMITIDO"
