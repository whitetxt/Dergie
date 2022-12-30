import discord, time, sys, os, traceback
from discord.ext import commands, tasks
from utils.config import Config
from utils.settings import Settings
from utils.status import *
from utils.helpers import *

_restart_bot_at_shutdown = False

start_time = time.time()

statuses = [
	discord.Activity(type=discord.ActivityType.playing, name="with you"),
	discord.Activity(type=discord.ActivityType.watching, name=f"{Status.members} users"),
	discord.Activity(type=discord.ActivityType.watching, name=f"{Status.servers} servers")
]

cur_status = -1

intents = discord.Intents.all()
bot = discord.AutoShardedBot(	owner_id=112633269010300928,
								intents=intents,
								status=statuses[0],
								debug_guilds=[1054875370924548167]
							)

@tasks.loop(minutes=1)
async def change_presence():
	global cur_status, statuses
	statuses = [
		discord.Activity(type=discord.ActivityType.playing, name="with you"),
		discord.Activity(type=discord.ActivityType.watching, name=f"{Status.members} users"),
		discord.Activity(type=discord.ActivityType.watching, name=f"{Status.servers} servers")
	]
	cur_status += 1
	if cur_status == len(statuses):
		cur_status = 0
	await bot.change_presence(status=discord.Status.online, activity=statuses[cur_status])

@tasks.loop(seconds=5)
async def send_status():
	Status.servers = len(bot.guilds)
	Status.members = len(bot.users)
	Status.ping = round(bot.latency * 1000, 2)
	Status.status = "Working Normally"
	await send_status_message(await bot.get_channel(1058507701946167398).fetch_message(1058508654694891551))

@bot.slash_command()
@commands.is_owner()
async def shutdown(ctx):
	global _restart_bot_at_shutdown
	await ctx.respond("Bye bye QwQ")
	await bot.change_presence(status=discord.Status.offline)
	await bot.close()
	_restart_bot_at_shutdown = False

@bot.slash_command()
@commands.is_owner()
async def restart(ctx):
	global _restart_bot_at_shutdown
	await ctx.respond("Alright, cya soon ;3")
	await bot.change_presence(status=discord.Status.idle)
	await bot.close()
	_restart_bot_at_shutdown = True

@bot.slash_command()
@commands.is_owner()
async def send_message(ctx, channel: discord.Option(str, "Channel ID") = None, content: discord.Option(str, "Message Content") = "Content!"):
	if channel is None or not channel.isnumeric():
		await ctx.respond(f"{Emojis.failure} Invalid channel ID.")
		return
	channel = int(channel)
	chan = bot.get_channel(channel)
	if chan is None:
		await ctx.respond(f"{Emojis.failure} Channel not found.")
		return

	await chan.send(content)
	await ctx.respond(f"{Emojis.success} Message sent!")

IgnoreImport = []

start_time = time.time()
cogs = lambda: [f.replace('.py', '') for f in os.listdir("cogs") if os.path.isfile(os.path.join("cogs", f))]

for Extension in cogs():
	if Extension in IgnoreImport:
		continue
	try:
		bot.load_extension(f"cogs.{Extension}")
		print(f"Extension {Extension} loaded.")
	except (discord.ClientException, ModuleNotFoundError):
		print(f'Failed to load extension {Extension}.')
		traceback.print_exc()

print(f"Cog loading took: {time.time() - start_time:.03f}s")

def cog_names(ctx: discord.AutocompleteContext):
	output = []
	for Extension in cogs():
		if Extension in IgnoreImport:
			continue
		if ctx.value in Extension:
			output.append(Extension)
	return output

@bot.slash_command()
@commands.is_owner()
async def reload(ctx, cog_name: discord.Option(str, description="Name of the cog to reload.", autocomplete=cog_names)):
	try:
		bot.reload_extension(f"cogs.{cog_name}")
		await ctx.respond(f"Reloaded `{cog_name}`")
	except (discord.ClientException, ModuleNotFoundError, commands.errors.ExtensionFailed) as e:
		await ctx.respond(f"Failed to reload `{cog_name}`\nError: {e}")

@bot.slash_command()
@commands.is_owner()
async def unload(ctx, cog_name: discord.Option(str, description="Name of the cog to unload.", autocomplete=cog_names)):
	try:
		bot.unload_extension(f"cogs.{cog_name}")
		await ctx.respond(f"Unloaded `{cog_name}`")
	except (discord.ClientException, ModuleNotFoundError, commands.errors.ExtensionFailed) as e:
		await ctx.respond(f"Failed to unload `{cog_name}`\nError: {e}")

@bot.slash_command()
@commands.is_owner()
async def load(ctx, cog_name: discord.Option(str, description="Name of the cog to load.", autocomplete=cog_names)):
	try:
		bot.load_extension(f"cogs.{cog_name}")
		await ctx.respond(f"Loaded `{cog_name}`")
	except (discord.ClientException, ModuleNotFoundError, commands.errors.ExtensionFailed) as e:
		await ctx.respond(f"Failed to load `{cog_name}`\nError: {e}")

@bot.event
async def on_ready():
	global start_time
	print(f"Connection took: {time.time() - start_time:.03f}s")
	start_time = time.time()
	bot.config = Config(bot)
	bot.settings = Settings(bot)
	send_status.start()
	change_presence.start()
	print(f"Startup took: {time.time() - start_time:.03f}s")
	print(f"Logged in as: {bot.user.name}#{bot.user.discriminator}")
	start_time = time.time()

@commands.Cog.listener()
async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
	if isinstance(error, commands.NotOwner):
		await ctx.respond(f"{Emojis.failure} You can't use this command!")
	elif isinstance(error, commands.MissingPermissions):
		await ctx.respond(f"{Emojis.failure} You don't have the required permissions for this command!")
	else:
		await ctx.respond(f"{Emojis.failure} Uh oh! An unknown error has occurred! Please report this at {Details.bug_report_url}")

# Testing Bot
start_time = time.time()
token = ""
with open("token.ini") as f:
	lines = f.readlines()
	lines = [line.replace("\n", "") for line in lines]
lines = [line for line in lines if not line.startswith("#") and line != ""]
if len(lines) == 0:
	print("No token found.")
	sys.exit(0)
token = lines[0]

bot.run(token)

if _restart_bot_at_shutdown:
	print("Restarting bot.")
	sys.exit(999)
else:
	sys.exit(0)