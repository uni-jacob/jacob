from tortoise import Tortoise

from jacob.config import get_database_url

TORTOISE_ORM = {
    "connections": {"default": get_database_url()},
    "apps": {
        "models": {
            "models": [
                "jacob.database.models",
                "aerich.models",
            ],
        },
    },
}


async def init_db_connection():
    await Tortoise.init(TORTOISE_ORM)
    await Tortoise.generate_schemas()
