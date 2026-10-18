from fastapi import Depends

# Domain interfaces
from app.domain.repositories.obra_repository import ObraRepository
from app.domain.repositories.seguridad_repository import SeguridadRepository
from app.domain.repositories.membresia_repository import MembresiaRepository
from app.domain.repositories.reporte_repository import ReporteRepository

# Persistence implementations
from app.persistence.repositories.cassandra_obra_repository import CassandraObraRepository
from app.persistence.repositories.cassandra_seguridad_repository import CassandraSeguridadRepository
from app.persistence.repositories.cassandra_membresia_repository import CassandraMembresiaRepository
from app.persistence.repositories.cassandra_reporte_repository import CassandraReporteRepository

# Domain services
from app.domain.services.obra_service import ObraService
from app.domain.services.seguridad_service import SeguridadService
from app.domain.services.membresia_service import MembresiaService
from app.domain.services.reporte_service import ReporteService

# Repository singletons for efficient prepared statement reuse across requests
_obra_repo = CassandraObraRepository()
_seguridad_repo = CassandraSeguridadRepository()
_membresia_repo = CassandraMembresiaRepository()
_reporte_repo = CassandraReporteRepository()


# --- Repository Providers ---
def get_obra_repository() -> ObraRepository:
    return _obra_repo


def get_seguridad_repository() -> SeguridadRepository:
    return _seguridad_repo


def get_membresia_repository() -> MembresiaRepository:
    return _membresia_repo


def get_reporte_repository() -> ReporteRepository:
    return _reporte_repo


# --- Domain Service Providers ---
def get_obra_service(
    repo: ObraRepository = Depends(get_obra_repository)
) -> ObraService:
    return ObraService(repo)


def get_seguridad_service(
    repo: SeguridadRepository = Depends(get_seguridad_repository)
) -> SeguridadService:
    return SeguridadService(repo)


def get_membresia_service(
    repo: MembresiaRepository = Depends(get_membresia_repository)
) -> MembresiaService:
    return MembresiaService(repo)


def get_reporte_service(
    repo: ReporteRepository = Depends(get_reporte_repository)
) -> ReporteService:
    return ReporteService(repo)
