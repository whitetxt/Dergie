import os
import discord
from discord.ext import commands
from discord.commands import Option
from utils.database import DictDB
from utils.helpers import Emojis
from utils.logger import Logger


class LoggerCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    log = discord.commands.SlashCommandGroup("log", "Controls bot logging")

    @log.command(description="Sets the channel which the bot will log to.")
    @commands.guild_only()
    async def set(
        self,
        ctx: discord.ApplicationContext,
        type: Option(
            str,
            description="The type of log to use this channel for.",
            choices=["user", "server", "messages"],
        ),
    ):
        Logger.set_channel(ctx.guild_id, ctx.channel_id, type)
        await ctx.respond(
            f"{Emojis.success} This channel has been set as the logging channel!"
        )

    @log.command(description="Creates logging channels and assigns them.")
    @commands.guild_only()
    async def setup(self, ctx: discord.ApplicationContext):
        msg = await ctx.respond("[0/4] Creating category...")
        category = await ctx.guild.create_category("Logging Zone")
        await msg.edit_original_response(content="[1/4] Creating user logs channel...")
        user = await category.create_text_channel("user-logs")
        await msg.edit_original_response(
            content="[2/4] Creating server logs channel..."
        )
        server = await category.create_text_channel("server-logs")
        await msg.edit_original_response(
            content="[3/4] Creating message logs channel..."
        )
        messages = await category.create_text_channel("message-logs")
        await msg.edit_original_response(content="[4/4] Assigning channels...")
        Logger.set_channel(ctx.guild_id, user.id, "user")
        Logger.set_channel(ctx.guild_id, server.id, "server")
        Logger.set_channel(ctx.guild_id, messages.id, "messages")
        await msg.edit_original_response(
            content=f"{Emojis.success} Successfully setup logging channels!"
        )

    @log.command(description="Configures what the bot should log.")
    @commands.guild_only()
    async def configure(
        self,
        ctx: discord.ApplicationContext,
        ban: discord.Option(
            bool, description="Should I log bans?", required=False, default=None
        ),
        unban: discord.Option(
            bool, description="Should I log unbans?", required=False, default=None
        ),
    ):
        db = DictDB(os.path.join("databases", "settings.db"))
        cur = db.cursor()
        cur.execute(
            "UPDATE logs SET ban = ?, unban = ? WHERE server_id = ?",
            (1 if ban else None, 1 if unban else None, ctx.guild_id),
        )
        db.commit()
        cur.close()
        db.close()
        await ctx.respond(f"{Emojis.success} Successfully updated log settings!")


def setup(bot):
    bot.add_cog(LoggerCog(bot))
