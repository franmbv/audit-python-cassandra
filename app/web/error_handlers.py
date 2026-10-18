import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.exceptions.domain_exceptions import (
    DomainException,
    EntityNotFoundError,
    BusinessRuleConflictError,
    DatabaseConnectionError,
    AuditIntegrityError,
)

logger = logging.getLogger("api")


def register_error_handlers(app: FastAPI) -> None:
    """Registers global exception handlers for domain, database, and validation errors."""

    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(_: Request, exc: EntityNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message},
        )

    @app.exception_handler(BusinessRuleConflictError)
    async def business_conflict_handler(_: Request, exc: BusinessRuleConflictError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message},
        )

    @app.exception_handler(DatabaseConnectionError)
    async def db_connection_handler(_: Request, exc: DatabaseConnectionError):
        logger.error("[API] Database infrastructure error: %s", exc.message)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "The audit service is currently unavailable. Please try again later."},
        )

    @app.exception_handler(AuditIntegrityError)
    async def audit_integrity_handler(_: Request, exc: AuditIntegrityError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.message},
        )

    @app.exception_handler(DomainException)
    async def generic_domain_handler(_: Request, exc: DomainException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.errors()},
        )
