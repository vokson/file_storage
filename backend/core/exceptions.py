### API

class ApiException(Exception):
    pass

class ParameterPathWrong(ApiException):
    pass


### FILE

class FileStorageException(Exception):
    pass

class FileNotFound(FileStorageException):
    pass
