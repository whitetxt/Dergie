import discord
from discord.ext import commands


def is_admin():
    async def predicate(ctx: discord.ApplicationContext):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)
