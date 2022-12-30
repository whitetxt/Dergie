import discord
from discord.ext import commands

class PrivateVC(commands.Cog):
	def __init__(self, bot: discord.AutoShardedBot):
		self.bot = bot
	
	privatevc = discord.commands.SlashCommandGroup("privatevc", "Managing User's private voice channels.")

	@privatevc.command(description="Setup private voice channels")
	async def setup(self, ctx: discord.ApplicationContext):

		return

	@privatevc.command(description="Creates a new private voice channel for a user.")
	async def create(self, ctx: discord.ApplicationContext):
		"""
		Responds with the bot's current ping.
		"""
		await ctx.respond(f"Hello :3\nMy ping is `{self.bot.latency:.04f}`s/`{self.bot.latency * 1000:.04f}`ms")

def setup(bot):
	bot.add_cog(PrivateVC(bot))