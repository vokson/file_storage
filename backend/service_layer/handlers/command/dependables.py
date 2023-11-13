from backend.domain import commands
from backend.service_layer.handlers.command import accounts, files, broker

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

    # BROKER
    commands.GetMessagesToBeSendToBroker: broker.get_not_executed_outgoing,
    commands.AddIncomingBrokerMessage: broker.add_incoming,
    commands.AddOutgoingBrokerMessage: broker.add_outgoing,
    commands.MarkBrokerMessageAsExecuted: broker.mark_as_executed,
    commands.ScheduleNextRetryForBrokerMessage: broker.schedule_next_retry,
    commands.PublishMessageToBroker: broker.publish,
}