import asyncio
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum

import discord
from discord import app_commands
from discord.ext import commands, tasks
from tortoise.transactions import in_transaction

from image_bot.models import ImageCollectionSettings, ImageCollectionPeriod, Image
from tortoise import Tortoise
import tortoise



class ImageCollection(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.check_weekly_collection.start()
        super().__init__()

    @app_commands.command(description="Set channel for image sending statistic collection")
    @app_commands.default_permissions(discord.Permissions(administrator=True))
    async def set_channel(self, interaction: discord.Interaction, target_channel: discord.TextChannel, result_channel: discord.TextChannel) -> None:
        try:
            await ImageCollectionSettings().create(
                guild=interaction.guild.id,
                collection_channel=target_channel.id,
                target_channel=result_channel.id)
        except tortoise.exceptions.IntegrityError:
            return await interaction.response.send_message("This channel is already set for image collection", ephemeral=True)
        await interaction.response.send_message(
            f"Collecting images from {target_channel.mention} and reporting to {result_channel.mention}", ephemeral=True
        )

    @app_commands.command(description="Disables image data collection.")
    @app_commands.default_permissions(discord.Permissions(administrator=True))
    async def disable_collection(self, interaction: discord.Interaction, target_channel: discord.TextChannel) -> None:
        await ImageCollectionSettings.filter(collection_channel=target_channel.id).delete()
        await interaction.response.send_message(
            f"Disabled collecting images from {target_channel.mention}", ephemeral=True
        )

    @app_commands.command(description="Ends period early and sets next period to end on Sunday")
    @app_commands.default_permissions(discord.Permissions(administrator=True))
    async def end_period(self, interaction: discord.Interaction) -> None:
        now = datetime.utcnow()
        await ImageCollectionPeriod.create(last_change=now)
        days_until_next_sunday = (6 - now.weekday()) % 7
        next_sunday = now + timedelta(days=days_until_next_sunday)

        await ImageCollectionPeriod.filter(guild=interaction.guild.id).update(last_change=next_sunday)
        await self.handle_period_reset(interaction.guild_id)
        await interaction.response.send_message(f"Period ended early", ephemeral=True)

    async def handle_period_reset(self, guild):
        data = await ImageCollectionSettings.filter(guild=guild)
        guild = self.bot.get_guild(guild)
        for d in data:
            print(data)
            collection_channel = guild.get_channel(d.collection_channel)
            target_channel = guild.get_channel(d.target_channel)
            embed = discord.Embed(title="Images sent for this week", description=f"Image collection report for channel {target_channel.mention}",
                                  color=discord.Color.blue())

            images_sent = await Image.filter(guild=guild.id, channel=d.target_channel)
            users = defaultdict(lambda : 0)
            total = 0
            for x in images_sent:
                users[x.user_id] += 1
                total += 1
                await x.delete()

            embed.add_field(name="Total images sent in period", value=total)
            await collection_channel.send(embed=embed)
            sorted_users = sorted(users.items(), key=lambda x: x[1], reverse=True)

            # Split into batches of 10
            batch_size = 10
            for i in range(0, len(sorted_users), batch_size):
                batch = sorted_users[i:i + batch_size]

                # Create embed
                embed = discord.Embed(title=f"Users [{i}-{i+batch_size}]", color=discord.Color.blue())

                # Format users in the embed
                description = "\n".join(
                    [f"**{i}.** <@{user_id}> `{count}`" for i, (user_id, count) in enumerate(batch, start=i + 1)])
                embed.description = description

                # Send the embed
                await collection_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.attachments:
            return  # Ignore bots and messages without attachments
        # Check if the message's channel is a target_channel in ImageCollectionSettings
        collection_setting = await ImageCollectionSettings.filter(target_channel=message.channel.id).first()
        if not collection_setting:
            return  # No collection setting for this channel
        for attachment in message.attachments:
            # Get the first image URL from the message
            image_url = attachment.url

            # Insert into the Image table
            async with in_transaction():
                await Image.create(
                    user_id=message.author.id,
                    channel=message.channel.id,
                    guild=message.guild.id if message.guild else 0,  # Handle DMs safely
                    link=image_url
                )

    @tasks.loop(minutes=1)  # Check every minute
    async def check_weekly_collection(self):
        """Periodically checks for image collection periods that are over a week old and updates them."""
        now = datetime.now()

        # Fetch all entries from ImageCollectionPeriod
        overdue_periods = await ImageCollectionPeriod.filter(
            last_change__lt=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        )
        for period in overdue_periods:
            # Perform the required function here
            await self.handle_period_reset(period.guild)

            # Calculate the next Sunday's date
            days_until_next_sunday = (6 - now.weekday()) % 7
            next_sunday = now + timedelta(days=days_until_next_sunday)
            next_sunday = next_sunday.replace(hour=0, minute=0, second=0, microsecond=0)

            # Update the period's 'last_change' to next Sunday's date
            await ImageCollectionPeriod.filter(guild=period.guild).update(last_change=next_sunday)

    def cog_unload(self):
        self.check_weekly_collection.cancel()  # Stop the task when the cog is unloaded


    @check_weekly_collection.before_loop
    async def before_tasks_start(self):
        """Wait for the bot to be ready before starting the task."""
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(ImageCollection(bot))
