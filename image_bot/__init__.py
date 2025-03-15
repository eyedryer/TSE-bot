from image_bot.config import sql_name, sql_password, postgres_db, connection_string

TORTOISE_ORM = {
    "connections": {"default": f"{connection_string}"},
    "apps": {
        "models": {
            "models": ["image_bot.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
