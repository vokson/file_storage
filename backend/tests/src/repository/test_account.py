import logging
from uuid import uuid4

import pytest
import pytest_asyncio

from backend.core import exceptions
from backend.tests.src.repository.mixins import AccountMixin

logger = logging.getLogger()


class TestAccount(AccountMixin):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, pg):
        await self._create_default_account(pg)

    @pytest.mark.asyncio
    async def test_get_by_auth_token(self, account_repository):
        model = await account_repository.get_by_token(
            self.DEFAULT_ACCOUNT_PARAMETERS["auth_token"]
        )
        assert dict(self.DEFAULT_ACCOUNT_PARAMETERS) == dict(model)

    @pytest.mark.asyncio
    async def test_get_if_not_exist(self, account_repository):
        with pytest.raises(exceptions.AccountNotFound):
            await account_repository.get_by_token(uuid4())
