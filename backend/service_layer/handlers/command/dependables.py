from backend.domain import commands
from backend.service_layer.handlers.command import accounts
from backend.service_layer.handlers.command import files

COMMAND_HANDLERS = {
    # ACCOUNT
    commands.GetAccountIdByAuthToken: accounts.get_account_id_by_auth_token,
    # FILE
    commands.GetFile: files.get,
    commands.DownloadFile: files.download,
    commands.UploadFile: files.upload,
}