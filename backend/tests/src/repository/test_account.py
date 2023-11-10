import logging
from uuid import uuid4

import pytest
import pytest_asyncio

from backend.core import exceptions
from backend.tests.src.repository.mixins import AccountMixin

logger = logging.getLogger()


class TestAccountRepository(AccountMixin):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, rollback_pg):
        await self._create_default_account(rollback_pg)

    @pytest.mark.asyncio
    async def test_get_by_auth_token(self, rollback_account_repository):
        model = await rollback_account_repository.get_by_token(
            self.DEFAULT_ACCOUNT_PARAMETERS["auth_token"]
        )
        assert dict(self.DEFAULT_ACCOUNT_PARAMETERS) == dict(model)

    @pytest.mark.asyncio
    async def test_get_if_not_exist(self, rollback_account_repository):
        with pytest.raises(exceptions.AccountNotFound):
            await rollback_account_repository.get_by_token(uuid4())
