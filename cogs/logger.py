import os
import discord
from discord.ext import commands
from utils.database import DictDB
from utils.helpers import Emojis
from utils.logger import Logger


class LoggerCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    log = discord.commands.SlashCommandGroup("log", "Controls bot logging")

    @log.command(description="Sets the channel which the bot will log to.")
    @commands.guild_only()
    async def set(self, ctx: discord.ApplicationContext):
        Logger.set_channel(ctx.guild_id, ctx.channel_id)
        await ctx.respond(
            f"{Emojis.success} This channel has been set as the logging channel!"
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
