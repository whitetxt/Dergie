import traceback
import discord
from utils.logger import Logger
from discord.ext import commands
from utils.helpers import Emojis, Details, format_username
from cogs.blacklist import Blacklisted
from utils.settings import Settings


class Listeners(commands.Cog):
    bot: discord.Bot

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.main_error_channel = 1240792436175933470

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
                f"{Emojis.failure} You have been blacklisted from using me for the following reason:\n{error}"
            )
        elif isinstance(error, discord.errors.CheckFailure):
            await ctx.respond(
                f"{Emojis.failure} A check has failed!\nError:{error.args}"
            )
        elif isinstance(error, commands.CommandError):
            await ctx.respond(
                f"{Emojis.failure} An error has occurred, and I don't know how to handle it! I'll report this to my owner."
            )
            channel = self.bot.get_channel(self.main_error_channel)
            await channel.send(f"{type(error)}\n{error}\n{ctx.command}\n{ctx.message}")
        else:
            await ctx.respond(
                f"{Emojis.failure} An error has occurred, and I don't know how to handle it! Please report this in the support server: {Details.support_url}."
            )
            channel = self.bot.get_channel(self.main_error_channel)
            await channel.send(f"{type(error)}\n{error}\n{ctx.command}\n{ctx.message}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        Settings.create_settings(guild.id)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        banAudit = None
        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                banAudit = entry
                break
        if banAudit is None:
            await Logger.ban(
                "Discord Ban", guild, user, reason="Unable to grab reason."
            )
            return
        await Logger.ban(
            banAudit.user,
            guild,
            user,
            reason=banAudit.reason if banAudit.reason is not None else "No reason",
        )

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        unbanAudit = None
        async for entry in guild.audit_logs(
            limit=5, action=discord.AuditLogAction.unban
        ):
            if entry.target.id == user.id:
                unbanAudit = entry
                break
        if unbanAudit is None:
            await Logger.unban(
                "Discord Unban", guild, user, reason="Unable to grab reason."
            )
            return
        await Logger.unban(
            unbanAudit.user,
            guild,
            user,
            reason=unbanAudit.reason if unbanAudit.reason is not None else "No reason",
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        kickAudit = None
        async for entry in member.guild.audit_logs(
            limit=5, action=discord.AuditLogAction.kick
        ):
            if entry.target.id == member.id:
                kickAudit = entry
                break
        if kickAudit is None:
            await Logger.kick(
                "Discord Kick", member.guild, member, reason="Unable to grab reason."
            )
            return
        await Logger.kick(
            kickAudit.user,
            member.guild,
            member,
            reason=kickAudit.reason if kickAudit.reason is not None else "No reason",
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await Logger.join(member.guild.id, member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await Logger.leave(member.guild.id, member)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        await Logger.channel_create(channel.guild.id, channel)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        await Logger.channel_delete(channel.guild.id, channel)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await Logger.message_edit(before, after)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        await Logger.message_delete(message)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await Logger.invite_create(invite)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await Logger.invite_delete(invite)


def setup(bot):
    bot.add_cog(Listeners(bot))
