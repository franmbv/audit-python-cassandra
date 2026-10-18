from app.domain.models.seguridad import SeguridadLog
from app.persistence.entities.seguridad_entity import SeguridadEntity


class SeguridadMapper:
    """Bi-directional translator between Cassandra physical entity and Seguridad domain model."""

    @staticmethod
    def to_domain(entity: SeguridadEntity) -> SeguridadLog:
        return SeguridadLog(
            login_usuario=entity.login_usuario,
            fecha_evento=entity.fecha_evento,
            accion=entity.accion,
            ip_origen=entity.ip_origen,
            detalles=entity.detalles,
            usuario_id=entity.usuario_id,
        )

    @staticmethod
    def to_entity(domain: SeguridadLog) -> SeguridadEntity:
        return SeguridadEntity(
            login_usuario=domain.login_usuario,
            fecha_evento=domain.fecha_evento,
            accion=domain.accion,
            ip_origen=domain.ip_origen,
            detalles=domain.detalles,
            usuario_id=domain.usuario_id,
        )

    @staticmethod
    def from_row(row) -> SeguridadLog:
        return SeguridadLog(
            login_usuario=row.login_usuario,
            fecha_evento=row.fecha_evento,
            accion=row.accion,
            ip_origen=getattr(row, "ip_origen", "127.0.0.1"),
            detalles=getattr(row, "detalles", None),
            usuario_id=row.usuario_id,
        )
