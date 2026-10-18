class DomainException(Exception):
    """Base exception for all audit microservice domain errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class EntityNotFoundError(DomainException):
    """Raised when an audit resource or record does not exist."""
    pass


class BusinessRuleConflictError(DomainException):
    """Raised when business rules or integrity constraints are violated."""
    pass


class DatabaseConnectionError(DomainException):
    """Raised when there are connectivity or initialization failures with the database engine."""
    pass


class AuditIntegrityError(DomainException):
    """Raised when audit records do not meet immutability or format requirements."""
    pass
