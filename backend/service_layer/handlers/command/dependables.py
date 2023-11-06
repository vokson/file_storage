from backend.domain import commands
from backend.service_layer.handlers.command import files, accounts

COMMAND_HANDLERS = {
    # ACCOUNT
    commands.GetAccountIdByAuthToken: accounts.get_account_id_by_auth_token,
    # FILE
    commands.GetFile: files.get,
    commands.DownloadFile: files.download,
    commands.UploadFile: files.upload,
    commands.DeleteFile: files.delete,
    commands.EraseFile: files.erase,
    # LINK
    # commands.AddLink: links.add_link,
}