from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.config.database import conexion_cassandra
from app.routes.membresias_routes import router as membresias_router
from app.routes.seguridad_routes import router as seguridad_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    conexion_cassandra.conectar()
    yield
    conexion_cassandra.cerrar()

app = FastAPI(
    title="Museo Atrium - Microservicio de Auditoría (Cassandra)",
    version="1.0.0",
    lifespan=lifespan
)


@app.exception_handler(RequestValidationError)
async def validacion_erronea_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": exc.errors()})

@app.get("/health", tags=["Salud"])
async def health_check():
    return {"status": "healthy", "service": "Cassandra Audit Service"}

app.include_router(seguridad_router)
app.include_router(membresias_router)