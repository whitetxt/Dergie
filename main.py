import discord, time, sys, os, traceback, json
from discord.ext import commands, tasks
from utils.config import Config
from utils.logger import Logger
from utils.settings import Settings
from utils.status import *
from utils.helpers import *

start_time = time.time()

ret_code = 0

statuses = [
    discord.Activity(type=discord.ActivityType.playing, name="with you"),
    discord.Activity(
        type=discord.ActivityType.watching, name=f"{Status.members} users"
    ),
    discord.Activity(
        type=discord.ActivityType.watching, name=f"{Status.servers} servers"
    ),
]

cur_status = -1

intents = discord.Intents.all()
bot = discord.Bot(
    owner_id=112633269010300928,
    intents=intents,
    status=statuses[0],
    debug_guilds=[692513145880576020, 1054875370924548167, 1240788846401163336],
)

bot.tasks = []


@tasks.loop(minutes=1)
async def change_presence():
    global cur_status, statuses
    statuses = [
        discord.Activity(type=discord.ActivityType.playing, name="with you"),
        discord.Activity(
            type=discord.ActivityType.watching, name=f"{Status.members} users"
        ),
        discord.Activity(
            type=discord.ActivityType.watching, name=f"{Status.servers} servers"
        ),
    ]
    cur_status += 1
    if cur_status == len(statuses):
        cur_status = 0
    await bot.change_presence(
        status=discord.Status.online, activity=statuses[cur_status]
    )


@tasks.loop(seconds=15)
async def send_status():
    Status.servers = len(bot.guilds)
    Status.members = len(bot.users)
    Status.ping = round(bot.latency * 1000, 2)
    Status.status = "Working Normally"
    channel = bot.get_channel(1058507701946167398)
    if channel is None:
        print("Failed to get status channel.")
        return
    try:
        msg = await channel.fetch_message(1058508654694891551)
    except:
        print("Failed to get status message.")
        return
    await send_status_message(msg)


@bot.slash_command()
@commands.is_owner()
async def shutdown(ctx):
    global ret_code
    await ctx.respond("Bye bye QwQ")
    ret_code = 0
    for task in bot.tasks:
        task.cancel()
    await bot.change_presence(status=discord.Status.offline)
    await bot.close()


@bot.slash_command()
@commands.is_owner()
async def restart(ctx):
    global ret_code
    await ctx.respond("Alright, cya soon ;3")
    ret_code = 1
    for task in bot.tasks:
        task.cancel()
    await bot.change_presence(status=discord.Status.idle)
    await bot.close()


ignore_import = ["reactions", "template"]

start_time = time.time()
cogs = lambda: [
    f.replace(".py", "")
    for f in os.listdir("cogs")
    if os.path.isfile(os.path.join("cogs", f))
]

for Extension in cogs():
    if Extension in ignore_import:
        continue
    try:
        bot.load_extension(f"cogs.{Extension}")
        print(f"Extension {Extension} loaded.")
    except (discord.ClientException, ModuleNotFoundError):
        print(f"Failed to load extension {Extension}.")
        traceback.print_exc()

print(f"Cog loading took: {time.time() - start_time:.03f}s")


@bot.event
async def on_ready():
    global start_time
    print(f"Connection took: {time.time() - start_time:.03f}s")
    start_time = time.time()
    bot.settings = Settings(bot)
    Config.bot = bot
    Logger.bot = bot
    bot.tasks += [send_status, change_presence]
    for task in bot.tasks:
        task.start()
    print(f"Startup took: {time.time() - start_time:.03f}s")
    print(f"Logged in as: {format_username(bot.user)}")
    start_time = time.time()


@commands.Cog.listener()
async def on_application_command_error(
    self, ctx: discord.ApplicationContext, error: discord.DiscordException
):
    if isinstance(error, commands.NotOwner):
        await ctx.respond(f"{Emojis.failure} You can't use this command!")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.respond(
            f"{Emojis.failure} You don't have the required permissions for this command!"
        )
    else:
        await ctx.respond(
            f"{Emojis.failure} Uh oh! An unknown error has occurred! Please report this at {Details.bug_report_url}"
        )


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
print(ret_code)
sys.exit(ret_code)
