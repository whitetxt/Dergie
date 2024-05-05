import discord
import json
import os
import time
import sqlite3
from typing import Dict

from utils.database import DictDB


class ServerSettings:
    database: str

    server_id: int

    automod_enabled: bool

    user_log_id: int | None
    guild_log_id: int | None
    message_log_id: int | None

    def __init__(self, database: str, server_id: int):
        self.database = database
        self.server_id = server_id

        self.automod_enabled = True
        self.user_log_id = None

    def load_from_database(self):
        db = DictDB(self.database)

        result = db.fetchall(
            "SELECT * FROM settings WHERE server_id = ?",
            (self.server_id,),
        )[0]
        self.automod_enabled = result["automod"] is not None
        self.user_log_id = result["user_log_id"]
        self.guild_log_id = result["guild_log_id"]
        self.message_log_id = result["message_log_id"]
        db.close()

    def save(self) -> None:
        print(self.database)
        db = sqlite3.connect(self.database)
        cursor = db.cursor()
        if (
            cursor.execute(
                "SELECT * FROM settings WHERE server_id = ?", (self.server_id,)
            ).fetchone()
            is None
        ):
            cursor.execute(
                "INSERT INTO settings(server_id, automod, user_log_id, guild_log_id, message_log_id) VALUES (?,?,?,?)",
                (
                    self.server_id,
                    "yes" if self.automod_enabled else None,
                    self.user_log_id,
                    self.guild_log_id,
                    self.message_log_id,
                ),
            )
        else:
            cursor.execute(
                "UPDATE settings SET automod = ?, user_log_id = ?, guild_log_id = ?, message_log_id = ? WHERE server_id = ?",
                (
                    "yes" if self.automod_enabled else None,
                    self.user_log_id,
                    self.guild_log_id,
                    self.message_log_id,
                    self.server_id,
                ),
            )
        db.commit()
        cursor.close()
        db.close()


class Settings:
    bot: discord.Bot

    database_path: str = "databases/settings.db"

    server_settings: Dict[int, ServerSettings] = {}

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.database_path = os.path.join("databases", "settings.db")
        # Perform initial database structure check.
        db = DictDB(self.database_path)

        # Load settings for each server
        for server in db.fetchall("SELECT server_id FROM servers"):
            server = server["server_id"]
            self.server_settings[server] = ServerSettings(self.database_path, server)
            self.server_settings[server].load_from_database()

        for g in bot.guilds:
            guild_id = g.id
            if guild_id not in self.server_settings:
                print(f"Creating new settings for `{g.name}`...")
                self.create_settings(guild_id)

        db.close()

    @classmethod
    def create_settings(cls, guild_id: int) -> None:
        """Generates a settings object for a guild.

        Args:
            guild_id (int): Guild ID
        """
        if guild_id in cls.server_settings:
            return
        cls.server_settings[guild_id] = ServerSettings(cls.database_path, guild_id)
        cls.server_settings[guild_id].save()

    @classmethod
    def get_settings(cls, guild_id: int) -> ServerSettings | None:
        """Gets the server settings for the specified guild ID

        Args:
            guild_id (int): The ID for the guild

        Returns:
            ServerSettings | None
        """
        if cls.server_settings.get(guild_id) is None:
            cls.create_settings(guild_id)
        return cls.server_settings[guild_id]
