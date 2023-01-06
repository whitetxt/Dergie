import discord
from datetime import datetime

class Status:
	ping: float = -1
	status: str = "Running"
	servers: int = -1
	members: int = -1

async def send_status_message(message: discord.Message):
	if message is None:
		print("Status message is None.")
		return
	emb = discord.Embed(title="My Status :3", description=f"Last Generated at {datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')} UTC", color=discord.Color(0xf5abb9))
	emb.add_field(name="Status", value=Status.status, inline=True)
	emb.add_field(name="Ping", value=f"{Status.ping} ms", inline=True)
	emb.add_field(name="Servers", value=f"In {Status.servers} servers", inline=True)
	emb.add_field(name="Members", value=f"Can see {Status.members} members", inline=True)
	await message.edit(content="Hi! Here is how I'm doing:", embed=emb)