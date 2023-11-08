from backend.domain import commands
from backend.service_layer.handlers.command import accounts, files

COMMAND_HANDLERS = {
    # ACCOUNT
    commands.GetAccountIdByAuthToken: accounts.get_account_id_by_auth_token,

    # FILE
    commands.GetFile: files.get,
    commands.DownloadFile: files.download,

    commands.AddFile: files.add,
    commands.UploadFile: files.upload,

    commands.DeleteFile: files.delete,
    commands.EraseFile: files.erase,
}