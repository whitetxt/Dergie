import discord
from discord.ext import commands
from utils.checks import *
from utils.helpers import Emojis
from utils.database import DictDB


class Perms(commands.Cog):
    def __init__(self, bot: discord.AutoShardedBot):
        self.bot = bot

    perms = discord.commands.SlashCommandGroup(
        "permissions", "Managing server's permissions"
    )

    admin = perms.create_subgroup("admin", "Manages admin roles")

    mod = perms.create_subgroup("mod", "Manages mod roles")

    @admin.command(description="Adds a role or user to the Admin class")
    @is_admin()
    async def add(
        self,
        ctx: discord.ApplicationContext,
        role: discord.Option(
            discord.Role, description="The role to add as an admin", default=None
        ),
        user: discord.Option(
            discord.Member, description="The user to add as an admin", default=None
        ),
    ):
        role: discord.Role = role
        user: discord.Member = user
        if role is None and user is None:
            await ctx.respond(
                f"{Emojis.failure} You must specify either a role or a user!"
            )
            return
        admin_type = "role" if role is not None else "user"
        msg = await ctx.respond(f"[0%] Fetching {admin_type} information...")
        db = DictDB("databases/permissions.db")
        admin_id = role.id if role is not None else user.id
        where = f"{admin_type}_id = {admin_id}"
        res = db.fetchall(f"SELECT * FROM permissions WHERE {where}")
        if res != []:
            await msg.edit_original_response(
                content=f"{Emojis.failure} This {admin_type} is already an admin!"
            )
            return
        await msg.edit_original_response(
            content=f"[50%] Adding {admin_type} as an admin..."
        )
        db.insert(
            f"INSERT INTO permissions(server_id, {admin_type}_id, permission_level) VALUES(?, ?, ?)",
            (ctx.guild.id, admin_id, Permissions.admin),
        )
        await msg.edit_original_response(
            content=f"{Emojis.success} {role.name} added as an admin!"
        )

    @admin.command(description="Removes a role or user to the Admin class")
    @is_admin()
    async def remove(
        self,
        ctx: discord.ApplicationContext,
        role: discord.Option(
            discord.Role, description="The role to remove as an admin", default=None
        ),
        user: discord.Option(
            discord.Member, description="The user to remove as an admin", default=None
        ),
    ):
        role: discord.Role = role
        user: discord.Member = user
        if role is None and user is None:
            await ctx.respond(
                f"{Emojis.failure} You must specify either a role or a user!"
            )
            return
        admin_type = "role" if role is not None else "user"
        msg = await ctx.respond(f"[0%] Fetching {admin_type} information...")
        db = DictDB("databases/permissions.db")
        admin_id = role.id if role is not None else user.id
        where = f"{admin_type}_id = {admin_id}"
        res = db.fetchall(f"SELECT * FROM permissions WHERE {where}")
        if res == []:
            await msg.edit_original_response(
                content=f"{Emojis.failure} This {admin_type} is not an admin!"
            )
            return
        await msg.edit_original_response(
            content=f"[50%] Removing {admin_type} as an admin..."
        )
        db.insert(
            f"DELETE FROM permissions WHERE {admin_type} = ?",
            (admin_id),
        )
        await msg.edit_original_response(
            content=f"{Emojis.success} {role.name} removed as an admin!"
        )

    @mod.command(description="Adds a role or user to the Moderator class")
    @is_mod()
    async def add(
        self,
        ctx: discord.ApplicationContext,
        role: discord.Option(
            discord.Role, description="The role to add as a mod", default=None
        ),
        user: discord.Option(
            discord.Member, description="The user to add as a mod", default=None
        ),
    ):
        role: discord.Role = role
        user: discord.Member = user
        if role is None and user is None:
            await ctx.respond(
                f"{Emojis.failure} You must specify either a role or a user!"
            )
            return
        mod_type = "role" if role is not None else "user"
        msg = await ctx.respond(f"[0%] Fetching {mod_type} information...")
        db = DictDB("databases/permissions.db")
        mod_id = role.id if role is not None else user.id
        where = f"{mod_type}_id = {mod_id}"
        res = db.fetchall(f"SELECT * FROM permissions WHERE {where}")
        if res != []:
            await msg.edit_original_response(
                content=f"{Emojis.failure} This {mod_type} is already an admin!"
            )
            return
        await msg.edit_original_response(
            content=f"[50%] Adding {mod_type} as a moderator..."
        )
        db.insert(
            f"INSERT INTO permissions(server_id, {mod_type}_id, permission_level) VALUES(?, ?, ?)",
            (ctx.guild.id, mod_id, Permissions.moderator),
        )
        await msg.edit_original_response(
            content=f"{Emojis.success} {role.name} added as an admin!"
        )

    @mod.command(description="Removes a role or user to the Moderator class")
    @is_mod()
    async def remove(
        self,
        ctx: discord.ApplicationContext,
        role: discord.Option(
            discord.Role, description="The role to remove as a mod", default=None
        ),
        user: discord.Option(
            discord.Member, description="The user to remove as a mod", default=None
        ),
    ):
        role: discord.Role = role
        user: discord.Member = user
        if role is None and user is None:
            await ctx.respond(
                f"{Emojis.failure} You must specify either a role or a user!"
            )
            return
        mod_type = "role" if role is not None else "user"
        msg = await ctx.respond(f"[0%] Fetching {mod_type} information...")
        db = DictDB("databases/permissions.db")
        (mod_id) = role.id if role is not None else user.id
        where = f"{mod_type}_id = {(mod_id)}"
        res = db.fetchall(f"SELECT * FROM permissions WHERE {where}")
        if res == []:
            await msg.edit_original_response(
                content=f"{Emojis.failure} This {mod_type} is not an admin!"
            )
            return
        await msg.edit_original_response(
            content=f"[50%] Removing {mod_type} as a moderator..."
        )
        db.insert(
            f"DELETE FROM permissions WHERE {mod_type} = ?",
            ((mod_id)),
        )
        await msg.edit_original_response(
            content=f"{Emojis.success} {role.name} removed as an moderator!"
        )


def setup(bot):
    bot.add_cog(Perms(bot))
