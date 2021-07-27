import os

from tortoise import Tortoise


async def init_db_connection():
    await Tortoise.init(
        db_url=os.getenv("LDATABASE_URL"),
        modules={
            "models": ["jacob.database.models"],
        },
    )
    await Tortoise.generate_schemas()
