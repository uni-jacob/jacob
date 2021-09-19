from tortoise import Tortoise

from jacob.services.common import get_database_url


async def init_db_connection():
    await Tortoise.init(
        db_url=get_database_url(),
        modules={
            "models": [
                "jacob.database.models.base",
                "jacob.database.models.schedule",
            ],
        },
    )
    await Tortoise.generate_schemas()
