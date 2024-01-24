from backend.core import exceptions

RESPONSE_CODES = {
    ConnectionResetError: (404, "Connection.Error.Reset"),
    exceptions.AuthTokenFail: (401, "Auth.Token.Fail"),
    exceptions.AccountNotFound: (401, "Account.Error.NotFound"),
    exceptions.TagNotFoundInAccount: (401, "Account.Error.Tag"),
    exceptions.NoSpaceInAccount: (507, "Account.Error.NoSpace"),
    exceptions.FileNotFound: (404, "File.Error.NotFound"),
    exceptions.RequestBodyNotJson: (400, "Request.Body.NotJson"),
    exceptions.ParameterBodyWrong: (400, "Parameter.Body.Wrong"),
    exceptions.ParameterPathWrong: (400, "Parameter.Path.Wrong"),
}
