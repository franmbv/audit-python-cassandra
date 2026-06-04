from pydantic import Field
from app.schemas.audit_schemas import AuditBaseSchema


class SeguridadSchema(AuditBaseSchema):
    login_usuario: str = Field(
        ...,
        description="Nombre de usuario que intenta acceder al sistema",
        examples=["jperez"]
    )

    evento_tipo: str = Field(
        ...,
        description="Tipo de evento de seguridad (LOGIN_EXITOSO, LOGIN_FALLIDO, etc.)",
        examples=["LOGIN_EXITOSO"]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "usuario_id": 1,
                "fecha_evento": "2026-06-01T08:15:00Z",
                "ip_origen": "192.168.1.10",
                "login_usuario": "jperez",
                "evento_tipo": "LOGIN_EXITOSO"
            }
        }
    }
