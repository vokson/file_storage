import logging

from backend.domain import commands
from backend.service_layer.uow import AbstractUnitOfWork

logger = logging.getLogger(__name__)


async def delete_expired(
    cmd: commands.DeleteExpiredLinks,
    uow: AbstractUnitOfWork,
):
    async with uow:
        await uow.link_repository.delete_expired()
        await uow.commit()
