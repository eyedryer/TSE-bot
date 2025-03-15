from discord.ext import commands
from discord.ext.commands import is_owner



class SyncCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.command()
    @is_owner()
    async def sync(self, ctx: commands.Context) -> None:
        await ctx.bot.tree.sync()
        await ctx.send("synced")


async def setup(bot):
    await bot.add_cog(SyncCommands(bot))
