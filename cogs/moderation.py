import discord
from discord.ext import commands
from discord.commands import Option

from utils.helpers import Emojis, format_username
from utils.logger import Logger


class Moderation(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(description="Kicks a member.")
    async def kick(
        self,
        ctx: discord.ApplicationContext,
        user: Option(discord.Member, description="Member to kick"),
        reason: Option(
            str, description="Reason for kick", default="No reason provided."
        ),
    ):
        user: discord.Member = user
        try:
            await ctx.guild.kick(
                user,
                reason=f"Kicked by {format_username(ctx.author)}. Reason: {reason}",
            )
            await ctx.respond(f"Successfully kicked {format_username(user)}!")
        except (discord.errors.Forbidden, discord.errors.HTTPException) as e:
            error_msg = "Unknown error."
            if isinstance(e, discord.errors.Forbidden):
                error_msg = "I do not have permission!"
            elif isinstance(e, discord.errors.HTTPException):
                error_msg = "Unknown. Please try again later."
            await ctx.respond(f"Couldn't kick {format_username(user)}: {error_msg}")

    @commands.slash_command(description="Bans a member.")
    async def ban(
        self,
        ctx: discord.ApplicationContext,
        user: Option(discord.Member, description="Member to ban"),
        reason: Option(
            str, description="Reason for ban", default="No reason provided."
        ),
    ):
        user: discord.Member = user
        try:
            msg = await ctx.respond(f"Attempting to ban {format_username(user)}...")
            await ctx.guild.ban(
                user,
                reason=f"Banned by {format_username(ctx.author)}. Reason: {reason}",
            )
            await Logger.ban(ctx.author, ctx.guild_id, user, reason)
            await msg.edit_original_response(
                content=f"Successfully banned {format_username(user)}!"
            )
        except (discord.errors.Forbidden, discord.errors.HTTPException) as e:
            error_msg = "Unknown error."
            if isinstance(e, discord.errors.Forbidden):
                error_msg = "I do not have permission!"
            elif isinstance(e, discord.errors.HTTPException):
                error_msg = "Unknown error. Please try again later."
            await msg.edit_original_response(
                content=f"Couldn't ban {format_username(user)}: {error_msg}"
            )

    @commands.slash_command(
        description="Unbans a user. Use their user ID to unban them."
    )
    async def unban(
        self,
        ctx: discord.ApplicationContext,
        user: Option(discord.User, description="User to unban"),
        reason: Option(
            str, description="Reason for unban", default="No reason provided."
        ),
    ):
        user: discord.User = user
        try:
            msg = await ctx.respond(f"Attempting to unban {format_username(user)}...")
            await ctx.guild.unban(
                user,
                reason=f"Unbanned by {format_username(ctx.author)}. Reason: {reason}",
            )
            await Logger.unban(ctx.author, ctx.guild_id, user, reason)
            await msg.edit_original_response(
                content=f"{Emojis.success} Successfully unbanned {format_username(user)}!"
            )
        except (discord.errors.Forbidden, discord.errors.HTTPException) as e:
            error_msg = f"Unknown error: {e}"
            if isinstance(e, discord.errors.Forbidden):
                error_msg = "I do not have permission!"
            elif "Unknown Ban" in e:
                error_msg = "This user is not banned!"
            await msg.edit_original_response(
                content=f"{Emojis.failure} Couldn't unban {format_username(user)}: {error_msg}"
            )

    @commands.slash_command(
        description="Purges the specified number of messages from a channel."
    )
    async def purge(
        self,
        ctx: discord.ApplicationContext,
        amount: Option(
            int, description="Number of messages to purge", min_value=1, max_value=100
        ),
        channel: Option(
            discord.TextChannel,
            description="Channel to purge in (Defaults to current channel)",
            required=False,
        ),
        reason: Option(
            str, description="Reason for purging", default="No reason provided."
        ),
        delete_bot: Option(bool, description="Only delete Bot messages", default=False),
    ):
        if channel is None:
            channel: discord.TextChannel = ctx.channel
        else:
            channel: discord.TextChannel = channel
        await ctx.respond(f"Purging {amount} messages, this may take a while...")

        def check(m: discord.Message):
            if delete_bot:
                return m.author.bot
            else:
                return True

        messages = await channel.purge(
            limit=amount,
            reason=f"Purged by {format_username(ctx.author)}. Reason: {reason}",
            bulk=True,
            check=check,
        )
        await Logger.purge(ctx.author, ctx.guild_id, channel, reason, len(messages))
        await ctx.channel.send(
            f"Successfully purged {len(messages)}/{amount} messages!"
        )


def setup(bot):
    bot.add_cog(Moderation(bot))
