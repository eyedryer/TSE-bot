import pathlib
from pathlib import Path

import aiohttp
import discord
from discord.app_commands import AppCommandError
from discord.ext import commands
from tortoise import Tortoise

from image_bot import config
from pkgutil import iter_modules
from image_bot import TORTOISE_ORM



class Main(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned,
                         intents=discord.Intents(guilds=True, members=True, messages=True, message_content=True),
                         application_id=config.application_id,
                         help_command=None)

    async def after_on_ready(self, bot):
        """Initialises bot specific guild commands."""
        await self.wait_until_ready()


    async def setup_hook(self):
        await bot.load_extension("cogs.image_collection")
        await bot.load_extension("cogs.sync")
        # creates https session for aiohttp
        self.session = aiohttp.ClientSession()
        await Tortoise.init(
            TORTOISE_ORM
        )


    async def close(self):
        await super().close()
        await self.session.close()
        await Tortoise.close_connections()


if __name__ == "__main__":
    bot = Main()
    bot.run(config.discord_token)
