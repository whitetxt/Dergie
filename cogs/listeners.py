import discord, os
from discord.ext import commands
from utils.helpers import Emojis, Details
from typing import Dict

class Listeners(commands.Cog):
	bot: discord.Bot

	userDBPath: str = os.path.join("databases", "users.db")
	blacklistedUsers: Dict[int, Dict[str, str | int]] = {}

	def __init__(self, bot: discord.Bot):
		self.bot = bot
		self.bot.add_check(self.blacklist)

	@commands.Cog.listener()
	async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
		if isinstance(error, commands.CommandOnCooldown):
			await ctx.respond(f"{Emojis.failure} This command is on cooldown! Please try again after {error.retry_after} seconds")
		elif isinstance(error, discord.errors.CheckFailure):
			await ctx.respond(f"{Emojis.failure} A check has failed! Perhaps you are blacklisted from using me?")
		elif isinstance(error, commands.CommandError):
			await ctx.respond(f"{Emojis.failure} An error has occurred, and I don't know how to handle it! I'll report this to my owner.")
		else:
			await ctx.respond(f"{Emojis.failure} An error has occurred, and I don't know how to handle it! Please report this in the support server: {Details.support_url}.")
			print(type(error))
			print(error)

	async def blacklist(self, ctx: discord.ApplicationContext):
		return not ctx.author.id in self.blacklistedUsers

	@commands.slash_command()
	@commands.is_owner()
	async def add_blacklist(self, ctx: discord.ApplicationContext, user_id: discord.Option(int), reason: discord.Option(str) = "No Reason"):
		if user_id in self.blacklistedUsers:
			await ctx.respond(f"{Emojis.failure} This user is already blacklisted!")
			return
		


def setup(bot):
	bot.add_cog(Listeners(bot))