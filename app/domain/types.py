class DomainError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status = status
        self.code = code
        self.message = message
        super().__init__(message)


def bad_request(message: str) -> DomainError:
    return DomainError(400, "bad_request", message)


def not_found() -> DomainError:
    return DomainError(404, "not_found", "Resource not found")
