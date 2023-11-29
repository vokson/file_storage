import logging
from uuid import UUID

from backend.core import exceptions
from backend.domain import commands
from backend.service_layer.uow import AbstractUnitOfWork

logger = logging.getLogger(__name__)


async def get_account_name_by_auth_token(
    cmd: commands.GetAccountNameByAuthToken,
    uow: AbstractUnitOfWork,
) -> UUID | None:
    async with uow:
        try:
            model = await uow.account_repository.get_by_token(cmd.auth_token)
            return model.name if model.is_active is True else None
        except exceptions.AccountNotFound:
            return None
