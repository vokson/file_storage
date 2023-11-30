from backend.domain import commands
from backend.service_layer.handlers.command import (accounts, broker, files,
                                                    links)

COMMAND_HANDLERS = {
    # ACCOUNT
    commands.GetAccounts: accounts.get_accounts,
    commands.GetAccountNameByAuthToken: accounts.get_account_name_by_auth_token,
    commands.UpdateAccountsActualSizes: accounts.update_accounts_actual_sizes,
    # FILE
    commands.GetFile: files.get,
    commands.GetStoredAndNotDeletedFiles: files.get_stored_and_not_deleted,
    commands.DownloadFile: files.download,
    commands.AddFile: files.add,
    commands.UploadFile: files.upload,
    commands.DeleteFile: files.delete,
    commands.EraseFile: files.erase,
    commands.CloneFile: files.clone,
    commands.EraseDeletedFiles: files.erase_deleted,
    # LINK
    commands.DeleteExpiredLinks: links.delete_expired,
    # BROKER
    commands.GetMessagesToBeSendToBroker: broker.get_not_executed_outgoing,
    commands.GetMessagesReceivedFromBroker: broker.get_not_executed_incoming,
    commands.DeleteExecutedBrokerMessages: broker.delete_executed,
    commands.AddIncomingBrokerMessage: broker.add_incoming,
    commands.AddOutgoingBrokerMessage: broker.add_outgoing,
    commands.ExecuteBrokerMessage: broker.execute,
    commands.MarkBrokerMessageAsExecuted: broker.mark_as_executed,
    commands.ScheduleNextRetryForBrokerMessage: broker.schedule_next_retry,
    commands.PublishMessageToBroker: broker.publish,
}
