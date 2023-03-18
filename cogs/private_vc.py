import discord
from discord.ext import commands
from utils.checks import *
from utils.helpers import Emojis


def privatevc_issetup():
    async def predicate(ctx: discord.ApplicationContext):
        return "Private VCs" in [category.name for category in ctx.guild.categories]
    return commands.check(predicate)


class PrivateVC(commands.Cog):
    def __init__(self, bot: discord.AutoShardedBot):
        self.bot = bot

    privatevc = discord.commands.SlashCommandGroup(
        "privatevc", "Managing User's private voice channels.")

    @privatevc.command(description="Setup private voice channels")
    @is_admin()
    async def setup(self, ctx: discord.ApplicationContext):
        if "Private VCs" in [category.name for category in ctx.guild.categories]:
            await ctx.respond(f"{Emojis.warning} Private Voice Channels are already setup! The category `Private VCs` will be used to create private voice channels.")
            return
        await ctx.guild.create_category("Private VCs")
        await ctx.respond(f"{Emojis.success} Private VCs category created! This server is now ready to use Private Voice Channels!")

    @privatevc.command(description="Creates a new private voice channel for a user.")
    @privatevc_issetup()
    async def create(self, ctx: discord.ApplicationContext):
        """
        Creates a new private voice channel for you!
        """
        for category, channels in ctx.guild.by_category():
            if category is None or category.name != "Private VCs":
                continue
            for channel in channels:
                if f"{ctx.author.name}#{ctx.author.discriminator}" not in channel.name:
                    continue
                await ctx.respond(f"{Emojis.warning} You already have a Private VC! Here it is for you: {channel.mention}")
                return
        category = [
            category for category in ctx.guild.categories if category.name == "Private VCs"][0]
        vc: discord.VoiceChannel = await ctx.guild.create_voice_channel(f"{ctx.author.name}#{ctx.author.discriminator} (1 users allowed)",
                                                                        reason="Dergie Private Voice Channels", category=category)
        perms = discord.PermissionOverwrite()
        perms.view_channel = False
        perms.connect = False
        await vc.set_permissions(ctx.guild.default_role, overwrite=perms, reason="Dergie Private Voice Channels")
        perms.view_channel = True
        perms.connect = True
        await vc.set_permissions(ctx.author, connect=True, view_channel=True, reason="Dergie Private Voice Channels")
        await ctx.respond(f"{Emojis.success} Voice Channel created {vc.mention}! You can now allow other people to join it!")

    @privatevc.command(description="Gives another user permission to join your voice channel.")
    @privatevc_issetup()
    async def add(self, ctx: discord.ApplicationContext, user: discord.Member):
        vc = None
        for category, channels in ctx.guild.by_category():
            if category is None or category.name != "Private VCs":
                continue
            for channel in channels:
                if f"{ctx.author.name}#{ctx.author.discriminator}" not in channel.name:
                    continue
                vc = channel
                break
            if vc is not None:
                break
        if vc is None:
            await ctx.respond(f"{Emojis.failure} You don't own a private voice channel! Please create one first.")
            return
        perms = discord.PermissionOverwrite()
        perms.view_channel = True
        perms.connect = True
        await vc.set_permissions(user, overwrite=perms, reason="Private Voice Channel - User Add")
        vc.permissions_for()
        prev_users = int(vc.name.replace(
            f"{ctx.author.name}#{ctx.author.discriminator} (", "").replace(" users allowed)", ""))
        await vc.edit(name=f"{ctx.author.name}#{ctx.author.discriminator} ({prev_users + 1} users allowed)")
        await ctx.respond(f"{Emojis.success} {user.name}#{user.discriminator} has been given permissions to join!")


def setup(bot):
    bot.add_cog(PrivateVC(bot))
