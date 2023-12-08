import logging
from contextlib import nullcontext as no_exception

import pytest
import pytest_asyncio

from backend.api.responses.accounts import AccountResponse
from backend.core.config import settings
from backend.tests.src.integration.mixins import CleanDatabaseMixin
from backend.tests.src.repository.mixins import AccountMixin

logger = logging.getLogger()


class TestAccountEndpoints(CleanDatabaseMixin, AccountMixin):
    def _accounts_url(self):
        return f"{self._base_url}/accounts/"

    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, pg):
        self._conn = pg
        self._base_url = settings.server
        await self.clean_db()

    @pytest.mark.asyncio
    async def test_get(self, session):
        await self._create_default_account(self._conn)

        async with session.get(self._accounts_url()) as r:
            assert r.status == 200

            with no_exception():
                arr = await r.json()
                assert type(arr) is list
                for x in arr:
                    AccountResponse(**x)

        await self.clean_db()
