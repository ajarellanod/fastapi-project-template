class ManagerException(Exception):
    """
    Base exception class with an error message and status code.
    """

    def __init__(self, detail: str, status_code: int = 500):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


class AlreadyExist(ManagerException):
    """
    Exception raised when an attempt to create an entity that already exists.
    """

    def __init__(self, detail: str = "Already exists"):
        super().__init__(detail, status_code=409)


class NotFound(ManagerException):
    """
    Exception raised when no result is found in a query.
    """

    def __init__(self, detail: str = "No result found"):
        super().__init__(detail, status_code=404)


class NoReference(ManagerException):
    """
    Exception raised when there is a problem with object references.
    """

    def __init__(self, detail: str = "Problem referencing others objects"):
        super().__init__(detail, status_code=409)
