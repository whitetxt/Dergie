import discord
from discord.ext import commands
from utils.logger import Logger


class Logger(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    log = discord.commands.SlashCommandGroup("log", "Controls bot logging")

    @log.command(description="Sets the channel which the bot will log to.")
    @commands.guild_only()
    async def set(self, ctx: discord.ApplicationContext):
        Logger.set_channel(ctx.guild_id, ctx.channel_id)


def setup(bot):
    bot.add_cog(Logger(bot))
