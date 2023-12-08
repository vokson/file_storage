import logging
from uuid import UUID

from backend.api.responses.accounts import AccountResponse
from backend.core import exceptions
from backend.domain import commands
from backend.service_layer.uow import AbstractUnitOfWork

logger = logging.getLogger(__name__)


async def get_accounts(
    cmd: commands.GetAccounts,
    uow: AbstractUnitOfWork,
) -> list[AccountResponse]:
    async with uow:
        models = await uow.account_repository.get_all()

    return [AccountResponse(**dict(x)) for x in models]


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


async def update_accounts_actual_sizes(
    cmd: commands.UpdateAccountsActualSizes,
    uow: AbstractUnitOfWork,
):
    async with uow:
        arr: list[
            tuple[str, int]
        ] = await uow.file_repository.get_actual_account_sizes()
        for account_name, size in arr:
            await uow.account_repository.update_actual_size(account_name, size)

        account_names = [x[0] for x in arr]
        await uow.account_repository.set_actual_size_for_excluded(
            account_names
        )

        await uow.commit()
