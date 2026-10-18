from app.domain.models.membresia import CodigoMembresia
from app.persistence.entities.membresia_entity import MembresiaEntity


class MembresiaMapper:
    """Bi-directional translator between Cassandra physical entity and Membresia domain model."""

    @staticmethod
    def to_domain(entity: MembresiaEntity) -> CodigoMembresia:
        return CodigoMembresia(
            id_comprador=entity.id_comprador,
            fecha_registro=entity.fecha_registro,
            codigo_seguridad=entity.codigo_seguridad,
            correo_envio=entity.correo_envio,
            estado=entity.estado,
        )

    @staticmethod
    def to_entity(domain: CodigoMembresia) -> MembresiaEntity:
        return MembresiaEntity(
            id_comprador=domain.id_comprador,
            fecha_registro=domain.fecha_registro,
            codigo_seguridad=domain.codigo_seguridad,
            correo_envio=domain.correo_envio,
            estado=domain.estado,
        )

    @staticmethod
    def from_row(row) -> CodigoMembresia:
        return CodigoMembresia(
            id_comprador=row.id_comprador,
            fecha_registro=row.fecha_registro,
            codigo_seguridad=row.codigo_seguridad,
            correo_envio=row.correo_envio,
            estado=row.estado,
        )
