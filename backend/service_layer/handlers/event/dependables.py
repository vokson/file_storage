from backend.domain import events
from backend.service_layer.handlers.event import files

EVENT_HANDLERS = {
    events.FileDeleted: [files.deleted],
    events.FileStored: [files.stored],
}
