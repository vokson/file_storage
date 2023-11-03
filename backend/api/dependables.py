from backend.service_layer.message_bus import get_message_bus


async def get_bus():
    return await get_message_bus(['db', 'file_repository'])
