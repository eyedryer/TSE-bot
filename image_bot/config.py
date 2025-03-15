import os

from dotenv import load_dotenv

load_dotenv()

discord_token = os.getenv("token")
application_id = os.getenv("application_id")
sql_password = os.getenv("POSTGRES_PASSWORD")
sql_name = os.getenv("POSTGRES_USER")
postgres_db = os.getenv("postgres_db")