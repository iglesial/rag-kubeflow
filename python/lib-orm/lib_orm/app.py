"""Application module for lib-orm."""

import asyncio

from sqlalchemy import text

from lib_orm.db import get_async_engine
from lib_orm.task_inputs import task_inputs


class App:
    """Diagnostic tool for database and ORM library."""

    def run(self) -> None:
        """
        Run diagnostics.

        Verify DB connectivity and print connection status.
        """
        db_url = task_inputs.db_url
        print(f"Database URL: {db_url}")
        asyncio.run(self._check_db(db_url))

    @staticmethod
    async def _check_db(url: str) -> None:
        """
        Check database connectivity.

        Parameters
        ----------
        url : str
            Database connection URL.
        """
        engine = get_async_engine(url)
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print("DB connection: OK")
        except Exception as exc:  # noqa: BLE001
            print(f"DB connection: FAILED ({exc})")
        finally:
            await engine.dispose()
