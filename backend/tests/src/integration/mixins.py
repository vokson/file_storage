class CleanDatabaseMixin:
    async def clean_db(self):
        async with self._conn.transaction():
            await self._conn.execute(
                """
                                TRUNCATE links CASCADE;
                                TRUNCATE files CASCADE;
                                TRUNCATE accounts CASCADE;
                                TRUNCATE broker_messages CASCADE;
                               """
            )
