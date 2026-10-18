from app.domain.models.obra import ObraHistorial
from app.persistence.entities.obra_entity import ObraEntity


class ObraMapper:
    """Bi-directional translator between Cassandra physical entity and Obra domain model."""

    @staticmethod
    def to_domain(entity: ObraEntity) -> ObraHistorial:
        return ObraHistorial(
            id_obra=entity.id_obra,
            fecha_evento=entity.fecha_evento,
            estatus_anterior=entity.estatus_anterior,
            estatus_nuevo=entity.estatus_nuevo,
            usuario_id=entity.usuario_id,
            ip_origen=entity.ip_origen,
        )

    @staticmethod
    def to_entity(domain: ObraHistorial) -> ObraEntity:
        return ObraEntity(
            id_obra=domain.id_obra,
            fecha_evento=domain.fecha_evento,
            estatus_anterior=domain.estatus_anterior,
            estatus_nuevo=domain.estatus_nuevo,
            usuario_id=domain.usuario_id,
            ip_origen=domain.ip_origen,
        )

    @staticmethod
    def from_row(row) -> ObraHistorial:
        return ObraHistorial(
            id_obra=row.id_obra,
            fecha_evento=row.fecha_evento,
            estatus_anterior=row.estatus_anterior,
            estatus_nuevo=row.estatus_nuevo,
            usuario_id=row.usuario_id,
            ip_origen=getattr(row, "ip_origen", "127.0.0.1"),
        )
