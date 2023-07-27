import discord
from discord.ext import commands

from utils.helpers import format_username


class General(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(description="Gets the bot's current ping.")
    async def ping(self, ctx: discord.ApplicationContext):
        """
        Responds with the bot's current ping.
        """
        await ctx.respond(
            f"Hello :3\nMy ping is `{self.bot.latency:.04f}`s/`{self.bot.latency * 1000:.04f}`ms"
        )

    @commands.slash_command(description="Retrieves information about a member.")
    async def info(
        self,
        ctx: discord.ApplicationContext,
        user: discord.Option(discord.Member, default=None),
    ):
        """
        Gets information about a member and displays it.
        """
        if user is None:
            user: discord.Member = ctx.author
        emb = discord.Embed(title=f"{format_username(user)}'s Information:")
        emb.set_thumbnail(url=user.avatar.url)
        emb.add_field(name="User ID:", value=f"{user.id}", inline=False)
        emb.add_field(name="Server Nickname:", value=f"{user.nick}")
        emb.add_field(
            name="Server Join Time:", value=f"<t:{int(user.joined_at.timestamp())}:F>"
        )
        emb.add_field(
            name="User Creation Time:",
            value=f"<t:{int(user.created_at.timestamp())}:F>",
            inline=False,
        )
        roles = [role.name for role in user.roles if "@everyone" not in role.name]
        rolesStr = ", ".join(roles)
        if rolesStr == "":
            rolesStr = "None"
        emb.add_field(name=f"Roles [{len(roles)}]:", value=rolesStr)
        emb.add_field(name="Top Role:", value=user.top_role)
        await ctx.respond(embed=emb)

    @commands.slash_command(description="Retrieves information about the server.")
    async def serverinfo(
        self,
        ctx: discord.ApplicationContext,
    ):
        """
        Gets information about the server and displays it.
        """
        guild: discord.Guild = ctx.guild
        emb = discord.Embed(title=f"{guild.name}'s Information:")
        emb.set_thumbnail(url=guild.icon.url)
        emb.add_field(name="Server ID:", value=f"{guild.id}", inline=False)
        emb.add_field(
            name="Creation Time:",
            value=f"<t:{int(guild.created_at.timestamp())}:F>",
        )
        emb.add_field(
            name="Owner:",
            value=f"{format_username(guild.owner)}",
            inline=False,
        )
        if ctx.guild.system_channel is None:
            emb.add_field(name="System channel:", value="None")
        else:
            emb.add_field(name="System channel:", value=ctx.guild.system_channel.name)
        emb.add_field(name="Text Channels:", value=len(guild.text_channels))
        emb.add_field(name="Voice Channels:", value=len(guild.voice_channels))
        bots = len([user for user in guild.members if user.bot])
        users = guild.member_count - bots
        emb.add_field(
            name="Total Members:",
            value=f"{guild.member_count} - {users} User{'s' if users != 1 else ''}, {bots} Bot{'s' if bots != 1 else ''}",
        )
        await ctx.respond(embed=emb)

    @commands.slash_command(description="Sends a member's avatar.")
    async def avatar(
        self,
        ctx: discord.ApplicationContext,
        user: discord.Option(discord.Member, default=None),
    ):
        """
        Gets a member's avatar and sends it.
        """
        if user is None:
            user: discord.Member = ctx.author
        await ctx.respond(f"{format_username(user)}'s avatar: {user.avatar.url}")


def setup(bot):
    bot.add_cog(General(bot))
