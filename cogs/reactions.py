import discord
import sqlite3
from typing import Dict
from discord.ext import commands
from utils.settings import *
from utils.helpers import *

class Reactions(commands.Cog):
	bot: discord.Bot

	def __init__(self, bot: discord.Bot):
		self.bot = bot

	@commands.slash_command(help="Creates a reaction role on a message, ")
	async def create_reaction_role(	self, ctx: discord.ApplicationContext, emoji: discord.Option(str, description="The emoji to use as the reaction", required=True), \
									message_content: discord.Option(str, description="Message content, leave blank to use existing message") = None):
		db = sqlite3.connect(os.path.join("databases", "reaction_roles.db"))
		cur = db.cursor()
		if message_content is None:
			await ctx.respond("Please reply to the message, or send a link to the message to add a reaction role to.")
			message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
			if message.reference is None:
				if not message.content.startswith("https://discord.com/channels"):
					await ctx.send(f"{Emojis.failure} You didn't reply to a message or give a link.")
					return
				else:
					m_id = int(message.content.split("/")[-1])
			else:
				m_id = int(message.reference.message_id)
			message = self.bot.get_message(m_id)
			if message is None:
				await ctx.send(f"{Emojis.failure} Couldn't find message with ID {m_id}, maybe I don't have permissions to see the channel?")
				return
			async with ctx.typing():
				await message.add_reaction(emoji)
		return

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

		if result is None or len(result) == 0: return

		role_id = result[0][0]
		role = guild.get_role(role_id)
		if role is None: return

		if payload.member.get_role(role_id) is None:
			try:
				payload.member.add_roles(role_id, reason=f"Reaction Role - Message ID {payload.message_id}")
				await payload.member.send(f"{Emojis.success} Role `{role.name}` added!")
			except (discord.HTTPException, discord.Forbidden):
				pass
	
	@commands.Cog.listener()
	@commands.guild_only()
	async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
		member = self.bot.get_user(payload.user_id)
		if member is None:
			member = await self.bot.fetch_user(payload.user_id)
			if member is None:
				return
		if member.bot: return
		guild = self.bot.get_guild(payload.guild_id)
		if guild is None: return

		emoji = payload.emoji.name
		if emoji is None: return

		db = sqlite3.connect(os.path.join("databases", "reaction_roles.db"))
		cur = db.cursor()
		result = cur.execute("SELECT role_id FROM reaction_roles WHERE message_id = ? AND emoji_id = ?", (payload.message_id, emoji)).fetchone()
		print(result)

		if result is None or len(result) == 0: return

		role_id = result[0][0]
		role = guild.get_role(role_id)
		if role is None: return

		if member.get_role(role_id) is not None:
			try:
				member.remove_roles(role_id, reason=f"Reaction Role - Message ID {payload.message_id}")
				await member.send(f"{Emojis.success} Role `{role.name}` removed!")
			except (discord.HTTPException, discord.Forbidden):
				pass

def setup(bot):
	bot.add_cog(Reactions(bot))