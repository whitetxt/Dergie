import discord
from discord.ext import commands


class Template(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(description="Gets the bot's current ping.")
    async def ping(self, ctx: discord.ApplicationContext):
        """
        Responds with the bot's current ping.
        """
        await ctx.respond(
            f"Hello :3\nMy ping is `{self.bot.latency:.04f}`s/`{self.bot.latency * 1000:.04f}`ms"
        )


def setup(bot):
    bot.add_cog(Template(bot))
