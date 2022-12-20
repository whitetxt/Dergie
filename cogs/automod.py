import discord
import requests
import re
from typing import List
from discord.ext import commands
from utils.settings import *
from utils.helpers import *

class AutoMod(commands.Cog):
	bot: discord.AutoShardedBot

	url_overrides: List[str] = []

	def __init__(self, bot: discord.AutoShardedBot):
		self.bot = bot

	@commands.Cog.listener()
	@commands.guild_only()
	async def on_message(self, message: discord.Message):
		if message.author == self.bot.user: return
		if not message.guild: return
		guild = message.guild

		settings = Settings.get_settings(guild.id)
		if settings is None: return

		if settings.automod_enabled:
			await self.check_automod_trigger(message)

	async def check_automod_trigger(self, message: discord.Message):
		# Check for any dangerous URLs
		urls = self.check_bad_urls(message)
		if urls is not None:
			urls = [url for url in urls if url not in self.url_overrides]
			await message.delete()
			await message.author.send(f"""{Emojis.failure} Dergie Warning! {Emojis.failure}
Your recent message in `{message.guild.name}` has been deleted as it was determined to have a dangerous URL in it.
Please review what you are sending and try again!
Detected dangerous URLs: {", ".join([x["domain"] for x in urls])}

If you think this is a false positive, please open a ticket in the support server: {Details.support_url}""")

		return

	def check_bad_urls(self, message: discord.Message):
		urls = re.findall("(?:[A-z0-9](?:[A-z0-9-]{0,61}[A-z0-9])?\.)+[A-z0-9][A-z0-9-]{0,61}[A-z0-9]", message.content)
		if len(urls) == 0: return None
		req = requests.post("https://anti-fish.bitflow.dev/check", json={"message": message.content})
		if req.status_code != 200:
			if req.status_code != 404:
				print(f"Unknown return from anti-fish:\n{req.status_code} - {req.content}")
			return None
		
		js = req.json()
		if not js["match"]:
			return None
		return js["matches"]


def setup(bot):
	bot.add_cog(AutoMod(bot))