import discord
import sqlite3
from typing import Dict
from discord.ext import commands
from utils.settings import *
from utils.helpers import *

class Reactions(commands.Cog):
	bot: discord.AutoShardedBot

	def __init__(self, bot: discord.AutoShardedBot):
		self.bot = bot

	@commands.Cog.listener()
	@commands.guild_only()
	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		if payload.member.bot: return
		guild = self.bot.get_guild(payload.guild_id)
		if guild is None: return

		emoji = payload.emoji.name
		if emoji is None: return

		db = sqlite3.connect(os.path.join("databases", "reaction_roles.db"))
		cur = db.cursor()
		result = cur.execute("SELECT role_id FROM reaction_roles WHERE message_id = ? AND emoji_id = ?", (payload.message_id, emoji)).fetchone()
		print(result)

		if len(result) == 0: return

		role_id = result[0][0]
		role = guild.get_role(role_id)
		if role is None: return

		if payload.member.get_role(role_id) is None:
			try:
				payload.member.add_roles(role_id, reason=f"Reaction Role - Message ID {payload.message_id}")
				await payload.member.send(f"{Emojis.tick} Role `{role.name}` added!")
			except (discord.HTTPException, discord.Forbidden):
				pass

def setup(bot):
	bot.add_cog(Reactions(bot))