class ApiException(Exception):
    pass


class RepositoryException(Exception):
    pass


### API


class Ok(ApiException):
    pass


class AuthTokenFail(ApiException):
    pass


class ParameterPathWrong(ApiException):
    pass


class ParameterBodyWrong(ApiException):
    pass


class RequestBodyNotJson(ApiException):
    pass


### SYNCRONIZATION


class NoConnectionToServer(ApiException):
    pass


class FileSizeError(ApiException):
    pass


### ACCOUNT


class AccountNotFound(RepositoryException):
    pass


class TagNotFoundInAccount(RepositoryException):
    pass


class NoSpaceInAccount(RepositoryException):
    pass


### FILE


class FileNotFound(RepositoryException):
    pass
