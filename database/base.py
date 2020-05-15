import urllib.parse as urlparse

import asyncpg


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

    async def query(self, query: str, *args, fetchone=False, fetchall=False):

        await self.connect()

        if fetchone:
            result = await self.conn.fetchrow(query, *args)
        elif fetchall:
            result = await self.conn.fetch(query, *args)
        else:
            result = await self.conn.execute(query, *args)

        await self.conn.close()
        return result

    async def connect(self):
        self.conn = await asyncpg.connect(**self.db_auth)

    def close(self):
        self.conn.close()
