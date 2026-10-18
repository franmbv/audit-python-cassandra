from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.persistence.config.database import db_cassandra

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health check for the audit microservice")
async def health_check():
    """Checks service availability and active Cassandra cluster connectivity."""
    is_db_alive = db_cassandra.is_healthy()
    status_str = "healthy" if is_db_alive else "degraded"

    content = {
        "status": status_str,
        "service": "Cassandra Audit Service",
        "database": "connected" if is_db_alive else "disconnected",
    }

    status_code = status.HTTP_200_OK if is_db_alive else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=status_code, content=content)
