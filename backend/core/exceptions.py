class ApiException(Exception):
    pass


class RepositoryException(Exception):
    pass


### API


class AuthTokenFail(ApiException):
    pass


class ParameterPathWrong(ApiException):
    pass


### ACCOUNT


class AccountNotFound(RepositoryException):
    pass


### FILE


class FileNotFound(RepositoryException):
    pass
