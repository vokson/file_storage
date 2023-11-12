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

    # EVENT LOOP
    # commands.ConsumeMessageFromBroker: broker.consume_message_from_broker,
    # commands.GetMessagesToBeSendToBroker: broker.get_messages_to_be_send_to_broker,
    commands.SendMessageToBroker: broker.send_message_to_broker,
    # commands.MarkIncomingBrokerMessageAsExecuted: broker.mark_incoming_broker_message_as_executed,
    # commands.MarkOutgoingBrokerMessageAsExecuted: broker.mark_outgoing_broker_message_as_executed,
    # commands.ScheduleNextRetryForBrokerMessage: broker.schedule_next_retry_for_broker_message,
}