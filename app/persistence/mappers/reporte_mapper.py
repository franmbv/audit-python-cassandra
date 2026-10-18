from app.domain.models.reporte import ReporteFacturacion, ReporteMembresia
from app.persistence.entities.reporte_entity import ReporteFacturacionEntity, ReporteMembresiaEntity


class ReporteFacturacionMapper:
    """Translator for periodic billing reports."""

    @staticmethod
    def to_domain(entity: ReporteFacturacionEntity) -> ReporteFacturacion:
        return ReporteFacturacion(
            anio=entity.anio,
            mes=entity.mes,
            id_factura=entity.id_factura,
            fecha_emision=entity.fecha_emision,
            id_comprador=entity.id_comprador,
            monto_neto=entity.monto_neto,
            iva_calculado=entity.iva_calculado,
            ganancia_museo=entity.ganancia_museo,
            estado=entity.estado,
        )

    @staticmethod
    def from_row(row) -> ReporteFacturacion:
        return ReporteFacturacion(
            anio=row.anio,
            mes=row.mes,
            id_factura=row.id_factura,
            fecha_emision=row.fecha_emision,
            id_comprador=row.id_comprador,
            monto_neto=row.monto_neto,
            iva_calculado=row.iva_calculado,
            ganancia_museo=row.ganancia_museo,
            estado=row.estado,
        )


class ReporteMembresiaMapper:
    """Translator for periodic membership reports."""

    @staticmethod
    def to_domain(entity: ReporteMembresiaEntity) -> ReporteMembresia:
        return ReporteMembresia(
            anio=entity.anio,
            mes=entity.mes,
            id_membresia=entity.id_membresia,
            fecha_registro=entity.fecha_registro,
            id_comprador=entity.id_comprador,
            codigo_membresia=entity.codigo_membresia,
            monto_cobrado=entity.monto_cobrado,
            estado=entity.estado,
        )

    @staticmethod
    def from_row(row) -> ReporteMembresia:
        return ReporteMembresia(
            anio=row.anio,
            mes=row.mes,
            id_membresia=row.id_membresia,
            fecha_registro=row.fecha_registro,
            id_comprador=row.id_comprador,
            codigo_membresia=row.codigo_membresia,
            monto_cobrado=row.monto_cobrado,
            estado=row.estado,
        )
