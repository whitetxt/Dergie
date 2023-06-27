from enum import IntEnum
import discord
from discord.ext import commands

from utils.database import DictDB

class Perms(IntEnum):
    admin = 3
    moderator = 2
    helper = 1
    user = 0

def is_admin():
    async def predicate(ctx: discord.ApplicationContext):
        if ctx.author.guild_permissions.administrator:
            return True
        db = DictDB("databases/permissions.db")
        for role in ctx.user.roles:
            data = db.fetchall("SELECT * FROM permissions WHERE role_id = ? AND server_id = ?", (role.id, ctx.guild.id))
            if data["permission_level"] >= Perms.admin:
                return True
        data = db.fetchall("SELECT * FROM permissions WHERE user_id = ? AND server_id = ?", (ctx.author.id, ctx.guild.id))
        return data["permission_level"] >= Perms.admin

    return commands.check(predicate)