from contextlib import asynccontextmanager
from traceback import format_exc

import aiopg
from psycopg2.extras import RealDictCursor

from src.config import Config as c

_DSN = f"host={c.POSTGRES_HOST} dbname={c.POSTGRES_DB} user={c.POSTGRES_USER} password={c.POSTGRES_PASSWORD}"
_TIMEOUT = 10


class PgConnection:
    def __init__(self):
        self._connection_pool = None

    async def get_connection_pool(self):
        if not self._connection_pool:
            self._connection_pool = await aiopg.create_pool(dsn=_DSN)

        return self._connection_pool

    async def close_connections(self):
        try:
            if self._connection_pool:
                self._connection_pool.close()
                await self._connection_pool.wait_closed()
        except:
            pass

    @asynccontextmanager
    async def cursor(self, cursor_factory=RealDictCursor, autocommit=True, **kwargs):
        pool = await self.get_connection_pool()

        async with pool.acquire() as conn:
            cursor = await conn.cursor(cursor_factory=cursor_factory, **kwargs)
            try:
                yield cursor
            except:
                print(format_exc())
            finally:
                cursor.close()


conn = PgConnection()
