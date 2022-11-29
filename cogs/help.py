import discord
import datetime
from discord.ext import commands, pages
from discord.commands import Option
from typing import Dict

def changelog_versions(self, ctx: discord.AutocompleteContext):
	versions = self.bot.config.changelog.keys()
	versions = list(filter(lambda x: ctx.value in x, versions))
	return versions

class Help(commands.Cog):
	def __init__(self, bot: discord.AutoShardedBot):
		self.bot = bot
		self.ignored_cogs = []

	def command_names(self, ctx: discord.AutocompleteContext):
		raw_cogs = dict(self.bot.cogs)
		cogs = []
		for cog_name in raw_cogs.keys():
			if cog_name not in self.ignored_cogs and ctx.value in cog_name:
				cogs.append(cog_name)
		return cogs

	@commands.slash_command()
	async def help(self, ctx: discord.ApplicationContext):
		"""Opens the help menu."""
		raw_cogs = dict(self.bot.cogs)
		cogs = {}
		for cog_name, cog in raw_cogs.items():
			if len(cog.get_commands()) == 0: continue
			if cog_name in self.ignored_cogs: continue
			cogs[cog_name] = cog

		paginator_pages = [
			discord.Embed(	title="Help Menu",
							colour=discord.Colour(0xffc8dd),
							timestamp=datetime.datetime.utcnow(),
							description="""Welcome to Dergie's help menu!

Dergie is a multi-purpose bot, with many features such as:
- Advanced Auto-Moderation
- Reaction Roles & Auto-Role
- Fun Games
- Fully Fledged Economy

This help menu is meant to assist Users and Admins with getting their heads around the many features that Dergie offers.

Use the buttons below to navigate!""")
		]
		for name, cog in cogs.items():
			emb = discord.Embed(title=f"Help for {name}",
								colour=discord.Colour(0xffc8dd),
								timestamp=datetime.datetime.utcnow())
			for command in cog.get_commands():
				emb.add_field(name=f"/{command.name}", value=command.description if command.description else "No help provided.", inline=False)
			paginator_pages.append(emb)

		paginator = pages.Paginator(
			pages=paginator_pages,
			show_indicator=True,
			use_default_buttons=False,
			timeout=60,
			custom_buttons=[
				pages.PaginatorButton("first", label="<<-", style=discord.ButtonStyle.success),
				pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.success),
				pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True),
				pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.success),
				pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.success),
			]
		)

		await paginator.respond(ctx.interaction, ephemeral=False)
	
	@commands.slash_command(description="Displays Dergie's current version.")
	async def version(self, ctx: discord.ApplicationContext):
		await ctx.respond(f"I am running v{self.bot.config.version}\nUse the changelog command to see what has changed!")

	@commands.slash_command(description="Displays Dergie's changelog")
	async def changelog(self, ctx: discord.ApplicationContext, version: Option(str, description="The version to display the changelog for", required=False, autocomplete=changelog_versions)):
		changelog: Dict[str, Dict[str, str]] = self.bot.config.changelog
		if version is not None:
			if version not in changelog:
				await ctx.respond(f"I couldn't find v{version}, are you sure it exists?")
			else:
				cl = changelog[version]
				embed = discord.Embed(title=f"v{version} - {cl['title']} ({cl['update_type']})", description=f"{cl['description']}")
				await ctx.respond(embed=embed)
			return

		paginator_pages = []
		for version, cl in changelog.items():
			paginator_pages.append(discord.Embed(title=f"v{version} - {cl['title']} ({cl['update_type']})",
								colour=discord.Colour(0xffc8dd),
								timestamp=datetime.datetime.utcnow(),
								description=f"{cl['description']}"))

		paginator = pages.Paginator(
			pages=paginator_pages,
			show_indicator=True,
			use_default_buttons=False,
			timeout=60,
			custom_buttons=[
				pages.PaginatorButton("first", label="<<-", style=discord.ButtonStyle.success),
				pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.success),
				pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=True),
				pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.success),
				pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.success),
			]
		)

		await paginator.respond(ctx.interaction, ephemeral=False)

def setup(bot):
	bot.add_cog(Help(bot))