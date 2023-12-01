from backend.service_layer.message_bus import get_message_bus


async def get_bus():
    return await get_message_bus(
        [
            "http",
            "db",
            "account_repository",
            "file_repository",
            "link_repository",
            "broker_message_repository",
        ]
    )
