import urllib.parse as urlparse

import asyncpg

from utils.exceptions import NotAllowedFetchType


class Base:
    def __init__(self, db_url):
        url = urlparse.urlparse(db_url)
        self.db_auth = {
            "user": url.username,
            "password": url.password,
            "host": url.hostname,
            "port": url.port,
            "database": url.path[1:],
        }
        self.conn = None

    async def query(self, query: str, *args, fetch=""):

        await self.connect()

        if fetch == "one":
            result = await self.conn.fetchrow(query, *args)
        elif fetch == "all":
            result = await self.conn.fetch(query, *args)
        elif fetch == "":
            result = await self.conn.execute(query, *args)
        else:
            raise NotAllowedFetchType(f"Неизвестный вариант fetch: {fetch}")

        await self.conn.close()
        return result

    async def connect(self):
        self.conn = await asyncpg.connect(**self.db_auth)

    def close(self):
        self.conn.close()
