import urllib.parse as urlparse

import psycopg2


class Base:
    def __init__(self, db_url, logs=False):
        self.logs = logs
        url = urlparse.urlparse(db_url)
        self.db_auth = {
            "user": url.username,
            "password": url.password,
            "host": url.hostname,
            "port": url.port,
            "database": url.path[1:],
        }
        self.conn, self.cur = None, None
        self.connect()

    def query(self, query: str, args=None, fetchone=False, fetchall=False):
        print(query) if self.logs else None
        commit_func = ["create", "insert", "delete", "update"]
        result_func = ["select", "returning"]
        self.cur.execute(query, args) if args else self.cur.execute(query)

        if any(func in query.lower() for func in commit_func):
            self.commit()

        if any(func in query.lower() for func in result_func):
            if not fetchone and not fetchall:
                fetchall = True

        if fetchone:
            return self.cur.fetchone()
        if fetchall:
            return self.cur.fetchall()
        return None

    def commit(self):
        self.conn.commit()

    def connect(self):
        self.conn = psycopg2.connect(**self.db_auth)
        self.cur = self.conn.cursor()

    def close(self):
        self.cur.close()
        self.conn.close()
