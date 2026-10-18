from app.web.routers.health import router as health_router
from app.web.routers.obras import router as obras_router
from app.web.routers.seguridad import router as seguridad_router
from app.web.routers.membresias import router as membresias_router
from app.web.routers.reportes import router as reportes_router

__all__ = [
    "health_router",
    "obras_router",
    "seguridad_router",
    "membresias_router",
    "reportes_router",
]
