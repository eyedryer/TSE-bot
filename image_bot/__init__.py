from image_bot.config import sql_name, sql_password, postgres_db

TORTOISE_ORM = {
    "connections": {"default": f"postgres://{sql_name}:{sql_password}@127.0.0.1:5432/{postgres_db}"},
    "apps": {
        "models": {
            "models": ["image_bot.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}