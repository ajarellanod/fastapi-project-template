class ManagerException(Exception):
    pass


class NotFound(ManagerException):
    pass


class AlreadyExists(ManagerException):
    pass


class NoReference(ManagerException):
    pass
