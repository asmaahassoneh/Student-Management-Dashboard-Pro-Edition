class ServiceError(Exception):
    """Base service-layer exception."""


class ValidationError(ServiceError):
    pass


class NotFoundError(ServiceError):
    pass


class ConflictError(ServiceError):
    pass


class PermissionDeniedError(ServiceError):
    pass
