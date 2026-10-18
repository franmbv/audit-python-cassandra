import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.persistence.config.database import db_cassandra
from app.web.error_handlers import register_error_handlers
from app.web.routers.health import router as health_router
from app.web.routers.obras import router as obras_router
from app.web.routers.seguridad import router as seguridad_router
from app.web.routers.membresias import router as membresias_router
from app.web.routers.reportes import router as reportes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: handles database initialization and graceful shutdown."""
    try:
        db_cassandra.conectar()
    except Exception as e:
        import logging
        logging.getLogger("api").warning(
            "Could not connect to Cassandra during startup. "
            "Reconnection will be attempted on demand: %s", e
        )
    yield
    db_cassandra.cerrar()


app = FastAPI(
    title="Atrium Museum - Audit Microservice (Cassandra)",
    description="Satellite microservice for traceability, security auditing, and analytical aggregations for Atrium Core.",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS Middleware Configuration
cors_origins_raw = os.getenv("CORS_ORIGINS", "*")
origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register domain and validation exception handlers
register_error_handlers(app)

# Include API routers
app.include_router(health_router)
app.include_router(seguridad_router)
app.include_router(obras_router)
app.include_router(membresias_router)
app.include_router(reportes_router)


@app.get("/", tags=["Root"])
def read_root():
    return {
        "status": "online",
        "service": "Museum Audit Microservice (Cassandra NoSQL)",
        "version": "2.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)