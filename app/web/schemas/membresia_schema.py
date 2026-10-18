from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class EstadoCodigoMembresia(str, Enum):
    EMITIDO = "EMITIDO"


class CodigoMembresiaCreateDTO(BaseModel):
    id_comprador: int = Field(..., description="Unique buyer identifier", examples=[1001])
    codigo_seguridad: str = Field(..., min_length=2, max_length=32, description="Issued security code", examples=["MK8X2Q9Z"])
    correo_envio: EmailStr = Field(..., description="Destination email address", examples=["buyer@example.com"])
    fecha_registro: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Issuance timestamp (UTC)"
    )
    estado: str = Field(default="EMITIDO", description="Functional state of the membership code")

    @field_validator("codigo_seguridad", mode="before")
    @classmethod
    def normalizar_codigo(cls, value: str) -> str:
        return value.strip().upper()


class CodigoMembresiaResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_comprador: int
    fecha_registro: datetime
    codigo_seguridad: str
    correo_envio: str
    estado: str


class PaginaCodigoMembresiaDTO(BaseModel):
    datos: List[CodigoMembresiaResponseDTO]
    paging_state: Optional[str] = None
