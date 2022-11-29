import discord
from discord.ext import commands
from discord.commands import Option

class Moderation(commands.Cog):
	def __init__(self, bot: discord.AutoShardedBot):
		self.bot = bot

	@commands.slash_command(description="Kicks a member.")
	async def kick(self, ctx: discord.ApplicationContext, user: Option(discord.Member, description="Member to kick"), reason: Option(str, description="Reason for kick", default="No reason provided.")):
		user: discord.Member = user
		try:
			await ctx.guild.kick(user, reason=f"Kicked by {ctx.author.display_name}#{ctx.author.discriminator}. Reason: {reason}")
			await ctx.respond(f"Successfully kicked {user.display_name}#{user.discriminator}!")
		except (discord.errors.Forbidden, discord.errors.HTTPException) as e:
			error_msg = "Unknown error."
			if isinstance(e, discord.errors.Forbidden):
				error_msg = "I do not have permission!"
			elif isinstance(e, discord.errors.HTTPException):
				error_msg = "Unknown. Please try again later."
			await ctx.respond(f"Couldn't kick {user.display_name}#{user.discriminator}: {error_msg}")

	@commands.slash_command(description="Bans a member.")
	async def ban(	self, ctx: discord.ApplicationContext,
					user: Option(discord.Member, description="Member to ban"),
					reason: Option(str, description="Reason for ban", default="No reason provided.")):
		user: discord.Member = user
		try:
			await ctx.guild.ban(user, reason=f"Banned by {ctx.author.display_name}#{ctx.author.discriminator}. Reason: {reason}")
			await ctx.respond(f"Successfully banned {user.display_name}#{user.discriminator}!")
		except (discord.errors.Forbidden, discord.errors.HTTPException) as e:
			error_msg = "Unknown error."
			if isinstance(e, discord.errors.Forbidden):
				error_msg = "I do not have permission!"
			elif isinstance(e, discord.errors.HTTPException):
				error_msg = "Unknown error. Please try again later."
			await ctx.respond(f"Couldn't ban {user.display_name}#{user.discriminator}: {error_msg}")
	
	@commands.slash_command(description="Purges the specified number of messages from a channel.")
	async def purge(self, ctx: discord.ApplicationContext,
					amount: Option(int, description="Number of messages to purge", min_value=1, max_value=100),
					channel: Option(discord.TextChannel, description="Channel to purge in (Defaults to current channel)", required=False),
					reason: Option(str, description="Reason for purging", default="No reason provided."),
					delete_bot: Option(bool, description="Only delete Dergie's messages", default=False)):
		if channel is None:
			channel: discord.TextChannel = ctx.channel
		else:
			channel: discord.TextChannel = channel
		sent_msg = await ctx.respond(f"Purging {amount} messages, this may take a while...")

		def check(m: discord.Message):
			if m.id == sent_msg.id:
				return False
			if delete_bot:
				return m.author == self.bot.user
			else:
				return True

		messages = await channel.purge(	limit=amount, reason=f"Purged by {ctx.author.display_name}#{ctx.author.discriminator}. Reason: {reason}",
										bulk=True, check=check)
		await ctx.respond(f"Successfully purged {len(messages)}/{amount} messages!")

def setup(bot):
	bot.add_cog(Moderation(bot))