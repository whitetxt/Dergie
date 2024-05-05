import discord
from utils.helpers import Emojis, format_username
from utils.settings import Settings


class Logger:
    bot: discord.Bot

    @classmethod
    def set_channel(cls, guild_id: int, channel_id: int, type: str) -> None:
        """Sets the channel to log all guild events to.

        Args:
            guild_id (int): The guild to set the log channel for.
            channel_id (int): The log channel's ID.
            type (str): The type of log to set the channel for.
        """
        setting = Settings.get_settings(guild_id)
        if type == "server":
            setting.guild_log_id = channel_id
        elif type == "user":
            setting.user_log_id = channel_id
        elif type == "messages":
            setting.message_log_id = channel_id
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
        return setting.user_log_id

    @classmethod
    async def get_user_channel(cls, guild_id: int) -> discord.TextChannel | None:
        """Gets the discord channel object for the log channel.

        Args:
            guild_id (int): The guild to get the log channel in.

        Returns:
            discord.TextChannel | None: The TextChannel if it exists, or None if it doesn't
        """
        setting = Settings.get_settings(guild_id)
        channel_id = setting.user_log_id
        if channel_id is None:
            return None
        channel = cls.bot.get_channel(channel_id)
        if channel is None:
            channel = await cls.bot.fetch_channel(channel_id)
            if channel is None:
                setting.user_log_id = None
                setting.save()
        return channel

    @classmethod
    async def get_guild_channel(cls, guild_id: int) -> discord.TextChannel | None:
        """Gets the discord channel object for the log channel.

        Args:
            guild_id (int): The guild to get the log channel in.

        Returns:
            discord.TextChannel | None: The TextChannel if it exists, or None if it doesn't
        """
        setting = Settings.get_settings(guild_id)
        channel_id = setting.guild_log_id
        if channel_id is None:
            return None
        channel = cls.bot.get_channel(channel_id)
        if channel is None:
            channel = await cls.bot.fetch_channel(channel_id)
            if channel is None:
                setting.guild_log_id = None
                setting.save()
        return channel

    @classmethod
    async def get_message_channel(cls, guild_id: int) -> discord.TextChannel | None:
        """Gets the discord channel object for the log channel.

        Args:
            guild_id (int): The guild to get the log channel in.

        Returns:
            discord.TextChannel | None: The TextChannel if it exists, or None if it doesn't
        """
        setting = Settings.get_settings(guild_id)
        channel_id = setting.message_log_id
        if channel_id is None:
            return None
        channel = cls.bot.get_channel(channel_id)
        if channel is None:
            channel = await cls.bot.fetch_channel(channel_id)
            if channel is None:
                setting.message_log_id = None
                setting.save()
        return channel

    @classmethod
    async def ban(
        cls,
        initiator: discord.User | str,
        guild_id: int,
        user: discord.User,
        reason: str = "",
        duration: str = "",
    ):
        channel = await cls.get_user_channel(guild_id)
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
        initiator: discord.User | str,
        guild_id: int,
        user: discord.User,
        reason: str = "",
    ):
        channel = await cls.get_user_channel(guild_id)
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
        initiator: discord.User | str,
        guild_id: int,
        purge_channel: discord.TextChannel,
        reason: str = "",
        no_of_messages: int = -1,
    ):
        channel = await cls.get_user_channel(guild_id)
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

    @classmethod
    async def kick(
        cls,
        initiator: discord.User | str,
        guild_id: int,
        user: discord.User,
        reason: str = "",
    ):
        channel = await cls.get_user_channel(guild_id)
        if channel is None:
            return
        embed = discord.Embed(
            title=f"{Emojis.warning} A member has been kicked {Emojis.warning}",
            colour=discord.Colour.orange(),
        )
        embed.add_field(name="User:", value=f"{user.mention} ({format_username(user)})")
        embed.add_field(
            name="Reason:", value=reason if reason != "" else "No reason provided"
        )
        if isinstance(initiator, (discord.User, discord.Member)):
            embed.set_footer(
                text=f"Kicked by {format_username(initiator)}",
                icon_url=initiator.display_avatar.url,
            )
        else:
            embed.set_footer(
                text=f"Kicked by {initiator}",
                icon_url=cls.bot.user.display_avatar.url,
            )
        await channel.send(embed=embed)

    @classmethod
    async def join(
        cls,
        guild_id: int,
        user: discord.User,
    ):
        channel = await cls.get_user_channel(guild_id)
        if channel is None:
            return
        embed = discord.Embed(
            title=f"A user has joined the server",
            colour=discord.Colour.green(),
            thumbnail=user.display_avatar.url,
        )
        embed.add_field(name="User:", value=f"{user.mention} ({format_username(user)})")
        embed.add_field(name="User ID:", value=f"{user.id}")
        embed.add_field(name="Account Created:", value=user.created_at.strftime("%c"))
        await channel.send(embed=embed)

    @classmethod
    async def leave(
        cls,
        guild_id: int,
        user: discord.User,
    ):
        channel = await cls.get_user_channel(guild_id)
        if channel is None:
            return
        embed = discord.Embed(
            title=f"A user has left the server",
            colour=discord.Colour.red(),
            thumbnail=user.display_avatar.url,
        )
        embed.add_field(name="User:", value=f"{user.mention} ({format_username(user)})")
        embed.add_field(name="User ID:", value=f"{user.id}")
        embed.add_field(name="Account Created:", value=user.created_at.strftime("%c"))
        embed.add_field(name="Joined at:", value=user.joined_at.strftime("%c"))
        await channel.send(embed=embed)

    @classmethod
    async def channel_create(
        cls,
        guild_id: int,
        channel: discord.abc.GuildChannel,
    ):
        log_channel = await cls.get_guild_channel(guild_id)
        if log_channel is None:
            return
        embed = discord.Embed(
            title="A channel has been created",
            colour=discord.Colour.green(),
        )
        embed.add_field(name="Channel Name:", value=f"{channel.name} ({channel.id})")
        await log_channel.send(embed=embed)

    @classmethod
    async def channel_delete(
        cls,
        guild_id: int,
        channel: discord.abc.GuildChannel,
    ):
        log_channel = await cls.get_guild_channel(guild_id)
        if log_channel is None:
            return
        embed = discord.Embed(
            title="A channel has been deleted",
            colour=discord.Colour.red(),
        )
        embed.add_field(name="Channel Name:", value=f"{channel.name} ({channel.id})")
        embed.add_field(name="Created At:", value=channel.created_at.strftime("%c"))
        await log_channel.send(embed=embed)

    @classmethod
    async def message_edit(
        cls,
        message_before: discord.Message,
        message_after: discord.Message,
    ):
        log_channel = await cls.get_message_channel(message_after.guild.id)
        if log_channel is None:
            return
        embed = discord.Embed(
            title="A message has been edited",
            colour=discord.Colour.orange(),
        )
        user = message_after.author
        embed.add_field(
            name="Author:", value=f"{user.mention} ({format_username(user)})"
        )
        embed.add_field(
            name="Channel:",
            value=f"{message_after.channel.mention} ({message_after.channel.id})",
            inline=False,
        )
        embed.add_field(name="Message Before:", value=message_before.content)
        embed.add_field(name="Message After:", value=message_after.content)
        await log_channel.send(embed=embed)

    @classmethod
    async def message_delete(
        cls,
        message: discord.Message,
    ):
        log_channel = await cls.get_message_channel(message.guild.id)
        if log_channel is None:
            return
        embed = discord.Embed(
            title="A message has been deleted",
            colour=discord.Colour.red(),
        )
        user = message.author
        embed.add_field(
            name="Author:", value=f"{user.mention} ({format_username(user)})"
        )
        embed.add_field(
            name="Channel:",
            value=f"{message.channel.mention} ({message.channel.id})",
            inline=False,
        )
        embed.add_field(name="Message:", value=message.content)
        await log_channel.send(embed=embed)
