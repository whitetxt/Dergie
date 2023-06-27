import traceback
import discord
from discord.ext import commands
from utils.helpers import Emojis, Details
from cogs.blacklist import Blacklisted


class Listeners(commands.Cog):
    bot: discord.Bot

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(
        self, ctx: discord.ApplicationContext, error: discord.DiscordException
    ):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(
                f"{Emojis.failure} This command is on cooldown! Please try again after {error.retry_after} seconds"
            )
        elif isinstance(error, Blacklisted):
            await ctx.respond(
                f"{Emojis.failure} You have been blacklisted from using Dergie for the following reason:\n{error}"
            )
        elif isinstance(error, discord.errors.CheckFailure):
            await ctx.respond(
                f"{Emojis.failure} A check has failed!\nError:{error.args}"
            )
        elif isinstance(error, commands.CommandError):
            await ctx.respond(
                f"{Emojis.failure} An error has occurred, and I don't know how to handle it! I'll report this to my owner."
            )
        else:
            await ctx.respond(
                f"{Emojis.failure} An error has occurred, and I don't know how to handle it! Please report this in the support server: {Details.support_url}."
            )
            print(type(error))
            print(error)
            traceback.print_exception(error)
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Listeners(bot))
