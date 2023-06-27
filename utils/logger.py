import discord
from utils.helpers import Emojis, format_username
from utils.settings import Settings


class Logger:
    bot: discord.Bot

    @classmethod
    def set_channel(cls, guild_id: int, channel_id: int) -> None:
        """Sets the channel to log all guild events to.

        Args:
            guild_id (int): The guild to set the log channel for.
            channel_id (int): The log channel's ID.
        """
        setting = Settings.get_settings(guild_id)
        setting.log_id = channel_id
        setting.save()

    @classmethod
    def get_channel_id(cls, guild_id: int) -> int | None:
        """Gets the log channel's ID for a guild.

        Args:
            guild_id (int): The guild to get the log channel ID

        Returns:
            int | None: The ID if it exists, or None if it doesn't.
        """
        setting = Settings.get_settings(guild_id)
        return setting.log_id

    @classmethod
    async def get_channel(cls, guild_id: int) -> discord.TextChannel | None:
        """Gets the discord channel object for the log channel.

        Args:
            guild_id (int): The guild to get the log channel in.

        Returns:
            discord.TextChannel | None: The TextChannel if it exists, or None if it doesn't
        """
        setting = Settings.get_settings(guild_id)
        channel_id = setting.log_id
        if channel_id is None:
            return None
        channel = cls.bot.get_channel(channel_id)
        if channel is None:
            channel = cls.bot.fetch_channel(channel_id)
            if channel is None:
                setting.log_id = None
                setting.save()
        return channel

    @classmethod
    async def ban(
        cls,
        initiator: discord.User,
        guild_id: int,
        user: discord.User,
        reason: str = "",
        duration: str = "",
    ):
        channel = await cls.get_channel(guild_id)
        if channel is None:
            return
        embed = discord.Embed(
            title=f"{Emojis.warning} A user has been banned {Emojis.warning}",
            colour=discord.Colour.red(),
        )
        embed.add_field(name="User:", value=f"{user.mention} ({format_username(user)})")
        embed.add_field(
            name="Reason:", value=reason if reason != "" else "No reason provided"
        )
        embed.add_field(
            name="Duration:", value=duration if duration != "" else "Permanent"
        )
        if isinstance(initiator, (discord.User, discord.Member)):
            embed.set_footer(
                text=f"Banned by {format_username(initiator)}",
                icon_url=initiator.display_avatar.url,
            )
        else:
            embed.set_footer(
                text=f"Banned by {initiator}", icon_url=cls.bot.user.display_avatar.url
            )
        await channel.send(embed=embed)

    @classmethod
    async def unban(
        cls,
        initiator: discord.User,
        guild_id: int,
        user: discord.User,
        reason: str = "",
    ):
        channel = await cls.get_channel(guild_id)
        if channel is None:
            return
        embed = discord.Embed(
            title=f"{Emojis.warning} A user has been unbanned {Emojis.warning}",
            colour=discord.Colour.green(),
        )
        embed.add_field(name="User:", value=f"{user.mention} ({format_username(user)})")
        embed.add_field(
            name="Reason:", value=reason if reason != "" else "No reason provided"
        )
        if isinstance(initiator, (discord.User, discord.Member)):
            embed.set_footer(
                text=f"Unbanned by {format_username(initiator)}",
                icon_url=initiator.display_avatar.url,
            )
        else:
            embed.set_footer(
                text=f"Unbanned by {initiator}",
                icon_url=cls.bot.user.display_avatar.url,
            )
        await channel.send(embed=embed)

    @classmethod
    async def purge(
        cls,
        initiator: discord.User,
        guild_id: int,
        purge_channel: discord.TextChannel,
        reason: str = "",
        no_of_messages: int = -1,
    ):
        channel = await cls.get_channel(guild_id)
        if channel is None:
            return
        embed = discord.Embed(
            title=f"{Emojis.warning} A channel has been purged {Emojis.warning}",
            colour=discord.Colour.orange(),
        )
        embed.add_field(
            name="Channel:", value=f"{purge_channel.mention} ({purge_channel.name})"
        )
        embed.add_field(
            name="Reason:", value=reason if reason != "" else "No reason provided"
        )
        embed.add_field(name="Messages Purged:", value=f"{no_of_messages} messages")
        if isinstance(initiator, (discord.User, discord.Member)):
            embed.set_footer(
                text=f"Purged by {format_username(initiator)}",
                icon_url=initiator.display_avatar.url,
            )
        else:
            embed.set_footer(
                text=f"Purged by {initiator}",
                icon_url=cls.bot.user.display_avatar.url,
            )
        await channel.send(embed=embed)
