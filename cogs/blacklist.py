import discord
import os
from discord.ext import commands
from discord.ext.pages import Page, Paginator
from utils.database import DictDB
from utils.helpers import Emojis, Details
from typing import Dict


class Blacklisted(commands.CheckFailure):
    pass


class Blacklist(commands.Cog):
    bot: discord.Bot

    path: str = os.path.join("databases", "users.db")
    users: Dict[int, str] = {}
    channelID: int = 1115354479794081914
    channel: discord.TextChannel
    blacklist = discord.commands.SlashCommandGroup(
        "blacklist", "Manages the global blacklist (OWNER USE ONLY)"
    )

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.load_blacklist()
        self.bot.add_check(self.in_blacklist)
        self.channel = self.bot.get_channel(self.channelID)
        if self.channel is None:
            self.channel = self.bot.fetch_channel(self.channelID)

    def load_blacklist(self):
        db = DictDB(self.path)
        result = db.fetchall("SELECT * FROM blacklist", [])
        for blacklist in result:
            self.users[blacklist["user_id"]] = blacklist["reason"]
        print(
            f"Loaded {len(result)} blacklisted user{'s' if len(result) != 1 else ''}."
        )

    async def in_blacklist(self, ctx: discord.ApplicationContext):
        if ctx.author.id in self.users:
            raise Blacklisted(self.users[ctx.author.id])
        return True

    @blacklist.command()
    @commands.is_owner()
    async def add(
        self,
        ctx: discord.ApplicationContext,
        user: discord.Option(discord.User),
        reason: discord.Option(str) = "No reason provided",
    ):
        if user.id in self.users:
            await ctx.respond(f"{Emojis.failure} This user is already blacklisted!")
            return
        user_id = user.id
        self.users[user_id] = reason
        db = DictDB(self.path)
        if db.exists("blacklist", "user_id", user_id):
            await ctx.responD(f"{Emojis.failure} This user is already blacklisted!")
        db.insert(
            "INSERT INTO blacklist(user_id, reason) VALUES (?, ?)", (user_id, reason)
        )
        embed = discord.Embed(
            title="Blacklist Update",
            description="A user has been added to the blacklist!",
            color=0xFF8000,
        )
        embed.add_field(
            name="Username",
            value=f"({user_id})\n{user.name}{f'#{user.discriminator}' if user.discriminator != '0' else ''}",
            inline=True,
        )
        embed.add_field(name="Reason", value=reason, inline=True)
        await self.channel.send(embed=embed)
        await ctx.respond(content="User added to the blacklist!")

    @blacklist.command()
    @commands.is_owner()
    async def remove(
        self,
        ctx: discord.ApplicationContext,
        user: discord.Option(discord.User),
        reason: discord.Option(str) = "No reason provided",
    ):
        if user.id not in self.users:
            await ctx.respond(f"{Emojis.failure} This user isn't blacklisted!")
            return
        user_id = user.id
        del self.users[user_id]
        db = DictDB(self.path)
        db.delete("DELETE FROM blacklist WHERE user_id = ?", (user_id,))
        embed = discord.Embed(
            title="Blacklist Update",
            description="A user has been removed from the blacklist!",
            color=0x00FF40,
        )
        embed.add_field(
            name="Username",
            value=f"({user_id})\n{user.name}{f'#{user.discriminator}' if user.discriminator != '0' else ''}",
            inline=True,
        )
        embed.add_field(name="Reason", value=reason, inline=True)
        await self.channel.send(embed=embed)
        await ctx.respond(content="User removed from the blacklist!")

    @blacklist.command()
    @commands.is_owner()
    async def list(self, ctx: discord.ApplicationContext):
        await ctx.respond("Building list... Please wait...")
        pages = []
        count = 0
        embed = discord.Embed(title="Blacklist")
        for user_id, reason in self.users.items():
            user = self.bot.get_user(user_id)
            if user is None:
                username = "Can't find user."
            else:
                username = f"{user.name}{f'#{user.discriminator}' if user.discriminator != '0' else ''}"
            embed.add_field(
                name=f"{user_id} ({username})", value=f"Reason: {reason}", inline=True
            )
            count += 1
            if count >= 25:
                pages.append(Page(embeds=[embed]))
                embed = discord.Embed(title="Blacklist")
                count = 0

        pages.append(Page(embeds=[embed]))
        page = Paginator(pages=pages)
        await page.respond(ctx.interaction)


def setup(bot):
    bot.add_cog(Blacklist(bot))
