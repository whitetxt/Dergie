import discord
import requests
import re
from typing import List
from discord.ext import commands
from utils.settings import *
from utils.helpers import *

class AutoMod(commands.Cog):
	bot: discord.Bot

	bad_url_overrides: List[str] = []

	def __init__(self, bot: discord.Bot):
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
			await message.delete()
			urls = [url for url in urls if url not in self.bad_url_overrides]
			if len(", ".join(x["domain"] for x in urls)) > 1000:
				urlsToSend = urls[0]["domain"]
				urls = urls[1:]
				while len(urlsToSend) < 1000 and len(urls) > 0:
					urlsToSend += ", " + urls[0]["domain"]
				urlsToSend = ", ".join(urlsToSend.split(", ")[:-1]) + " & more"
			else:
				urlsToSend = ", ".join(x["domain"] for x in urls)
			await message.author.send(f"""{Emojis.failure} Dergie Warning! {Emojis.failure}
Your recent message in `{message.guild.name}` has been deleted as it was determined to have dangerous URLs in it.
Please review what you are sending and try again!
Detected dangerous URLs: {urlsToSend}

If you think this is a false positive, please open a ticket in the support server: {Details.support_url}""")
		return

	def check_bad_urls(self, message: discord.Message):
		urls = re.findall("(?:[A-z0-9](?:[A-z0-9-]{0,61}[A-z0-9])?\\.)+[A-z0-9][A-z0-9-]{0,61}[A-z0-9]", message.content)
		if len(urls) == 0: return None
		req = requests.post("https://anti-fish.bitflow.dev/check", json={"message": message.content})
		if req.status_code != 200:
			if req.status_code != 404:
				print(f"Unknown return from anti-fish:\n{req.status_code} - {req.content}")
			return None
		
		js = req.json()
		if not js["match"]:
			return None
		js["matches"] = [url for url in js["matches"] if url not in self.bad_url_overrides]
		return js["matches"]


def setup(bot):
	bot.add_cog(AutoMod(bot))