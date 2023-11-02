from backend.domain import commands
from backend.service_layer.handlers.command import files

COMMAND_HANDLERS = {
    # FILE
    commands.DownloadFile: files.download,
}