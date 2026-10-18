from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MembresiaEntity(BaseModel):
    """Physical representation of records in table auditoria_codigos_membresia."""
    model_config = ConfigDict(from_attributes=True)

    id_comprador: int
    fecha_registro: datetime
    codigo_seguridad: str
    correo_envio: str
    estado: str = "EMITIDO"
