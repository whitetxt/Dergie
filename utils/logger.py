import discord
from utils.settings import Settings


class Logger:
    bot: discord.Bot

    def __init__(self, bot):
        self.bot = bot

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
        channel = cls.bot.get_channel(channel_id)
        if channel is None:
            channel = cls.bot.fetch_channel(channel_id)
            if channel is None:
                setting.log_id = None
                setting.save()
        return channel
