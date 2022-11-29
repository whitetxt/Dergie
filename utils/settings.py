import discord
import json
import os
import time
import sqlite3
from typing import Dict

class ServerSettings:
	database: str

	server_id: int
	server_name: str
	num_members: int

	automod_enabled: bool
	antifish_strength: float

	def __init__(self, database: str, server_id: int):
		self.database = database
		self.server_id = server_id

		self.server_name = ""
		self.num_members = 0

		self.automod_enabled = True
		self.antifish_strength = 0.85

	def load_from_database(self):
		db = sqlite3.connect(self.database)
		cursor = db.cursor()
		result = cursor.execute("SELECT name, num_members FROM servers WHERE server_id = ?", (self.server_id, )).fetchone()
		self.server_name = result[0]
		self.num_members = result[1]

		result = cursor.execute("SELECT automod, antifish_strength FROM settings WHERE server_id = ?", (self.server_id, )).fetchone()
		self.automod_enabled = result[0] is not None
		self.antifish_strength = result[1]
		cursor.close()
		db.close()

	def save(self) -> None:
		db = sqlite3.connect(self.database)
		cursor = db.cursor()
		if cursor.execute("SELECT * FROM servers WHERE server_id = ?", (self.server_id, )).fetchone() is None:
			cursor.execute("INSERT INTO servers(server_id, name, num_members) VALUES (?,?,?)", (self.server_id, self.server_name, self.num_members))
		else:
			cursor.execute("UPDATE servers SET name = ?, num_members = ? WHERE server_id = ?", (self.server_name, self.num_members, self.server_id))

		if cursor.execute("SELECT * FROM settings WHERE server_id = ?", (self.server_id, )).fetchone() is None:
			cursor.execute("INSERT INTO settings(server_id, automod) VALUES (?,?)", (self.server_id, "yes" if self.automod_enabled else None))
		else:
			cursor.execute("UPDATE settings SET automod = ? WHERE server_id = ?", ("yes" if self.automod_enabled else None, self.server_id))
		db.commit()
		cursor.close()
		db.close()

class Settings:
	bot: discord.AutoShardedBot

	database_path: str = ""

	server_settings: Dict[int, ServerSettings] = {}

	def __init__(self, bot: discord.AutoShardedBot):
		self.bot = bot
		self.database_path = os.path.join("databases", "settings.db")
		# Perform initial database structure check.
		db = sqlite3.connect(self.database_path)
		table_names = [t[0] for t in db.execute("SELECT name FROM sqlite_master WHERE type='table';")]
		expected_tables = {	"servers":
"""CREATE TABLE "servers" (
	"server_id"	INTEGER NOT NULL,
	"name"	TEXT,
	"num_members"	INTEGER DEFAULT 0,
	"join_time"	INTEGER DEFAULT 0,
	PRIMARY KEY("server_id")
);""",
							"settings": 
"""CREATE TABLE "settings" (
	"server_id"	INTEGER NOT NULL,
	"automod"	TEXT DEFAULT 'yes',
	"antifish_strength"	REAL NOT NULL DEFAULT 0.85,
	PRIMARY KEY("server_id"),
	FOREIGN KEY("server_id") REFERENCES "servers"("server_id")
);"""}

		cursor = db.cursor()
		for table, ddl in expected_tables.items():
			if table not in table_names:
				cursor.execute(ddl)
		
		# Load settings for each server
		for server in cursor.execute("SELECT server_id FROM servers").fetchall():
			server = server[0]
			self.server_settings[server] = ServerSettings(self.database_path, server)
			self.server_settings[server].load_from_database()

		for guild in bot.guilds:
			g = guild
			guild_id = g.id
			name = g.name
			member_count = g.member_count
			if guild_id in self.server_settings:
				self.server_settings[guild_id].server_name = name
				self.server_settings[guild_id].num_members = member_count
			else:
				print(f"Creating new settings for `{name}`...")
				self.create_settings(guild_id, name, member_count)
			self.server_settings[guild_id].save()

		cursor.close()
		db.close()

	def create_settings(self, guild_id: int, name: str, num_members: int) -> None:
		if guild_id in self.server_settings: return
		self.server_settings[guild_id] = ServerSettings(self.database_path, guild_id)
		self.server_settings[guild_id].server_name = name
		self.server_settings[guild_id].num_members = num_members
		self.server_settings[guild_id].save()

	@classmethod
	def get_settings(cls, guild_id: int) -> ServerSettings | None:
		if guild_id not in cls.server_settings[guild_id]:
			return None

		return cls.server_settings[guild_id]
