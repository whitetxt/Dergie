from io import StringIO
import sys
import time
import traceback
import discord, os, json
from discord.ext import commands
from utils.helpers import Emojis


class Owner(commands.Cog):
    ignore_import = ["reactions", "template"]

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    owner = discord.commands.SlashCommandGroup(
        "owner",
        "Owner only commands.",
        checks=[commands.is_owner().predicate],
        guild_ids=[1054875370924548167],
    )

    def cog_names(self, ctx: discord.AutocompleteContext):
        output = []
        cogs = lambda: [
            f.replace(".py", "")
            for f in os.listdir("cogs")
            if os.path.isfile(os.path.join("cogs", f))
        ]
        for Extension in cogs():
            if Extension in self.ignore_import:
                continue
            if ctx.value in Extension:
                output.append(Extension)
        return output

    @owner.command()
    async def eval(self, ctx: discord.ApplicationContext, to_eval: discord.Option(str)):
        msg = await ctx.respond("Evaluating expression...")
        error = None
        start = time.perf_counter_ns()
        orig = sys.stdout
        sys.stdout = StringIO("")
        try:
            result = eval(to_eval)
        except Exception as e:
            error = e
        taken = time.perf_counter_ns() - start
        taken /= 1000
        if error is not None:
            await msg.edit_original_response(
                content=f"An error occurred during evaluation.\nType: {type(error)}\n{error}\nTrace: {traceback.format_exc()}\nTime taken: {taken:.01f}ms"
            )
        else:
            await msg.edit_original_response(
                content=f"Evaluation result:\n```{result}```\nTime taken: {taken:.01f}ms"
            )

    @owner.command()
    async def reload(
        self,
        ctx,
        cog_name: discord.Option(
            str, description="Name of the cog to reload.", autocomplete=cog_names
        ),
    ):
        try:
            self.bot.reload_extension(f"cogs.{cog_name}")
            await ctx.respond(f"Reloaded `{cog_name}`")
        except (
            discord.ClientException,
            ModuleNotFoundError,
        ) as e:
            await ctx.respond(f"Failed to reload `{cog_name}`\nError: {e}")
        except discord.errors.ExtensionNotLoaded:
            try:
                self.bot.load_extension(f"cogs.{cog_name}")
                await ctx.respond(f"Reloaded `{cog_name}`")
            except (
                discord.ClientException,
                ModuleNotFoundError,
            ) as e:
                await ctx.respond(f"Failed to reload `{cog_name}`\nError: {e}")

    @owner.command()
    async def unload(
        self,
        ctx,
        cog_name: discord.Option(
            str, description="Name of the cog to unload.", autocomplete=cog_names
        ),
    ):
        try:
            self.bot.unload_extension(f"cogs.{cog_name}")
            await ctx.respond(f"Unloaded `{cog_name}`")
        except (
            discord.ClientException,
            ModuleNotFoundError,
        ) as e:
            await ctx.respond(f"Failed to unload `{cog_name}`\nError: {e}")

    @owner.command()
    async def load(
        self,
        ctx,
        cog_name: discord.Option(
            str, description="Name of the cog to load.", autocomplete=cog_names
        ),
    ):
        try:
            self.bot.load_extension(f"cogs.{cog_name}")
            await ctx.respond(f"Loaded `{cog_name}`")
        except (
            discord.ClientException,
            ModuleNotFoundError,
        ) as e:
            await ctx.respond(f"Failed to load `{cog_name}`\nError: {e}")

    @owner.command()
    async def send_message(
        self,
        ctx,
        channel: discord.Option(str, "Channel ID") = None,
        content: discord.Option(str, "Message Content") = "Content!",
    ):
        if channel is None or not channel.isnumeric():
            await ctx.respond(f"{Emojis.failure} Invalid channel ID.")
            return
        channel = int(channel)
        chan = self.bot.get_channel(channel)
        if chan is None:
            await ctx.respond(f"{Emojis.failure} Channel not found.")
            return

        await chan.send(content)
        await ctx.respond(f"{Emojis.success} Message sent!")

    @owner.command()
    async def send_embed(
        self,
        ctx,
        channel: discord.Option(str, "Channel ID") = None,
        embed: discord.Option(str, "Embed, in JSON") = None,
    ):
        if channel is None or not channel.isnumeric():
            await ctx.respond(f"{Emojis.failure} Invalid channel ID.")
            return
        if embed is None:
            await ctx.respond(
                f"{Emojis.failure} You need to give me something to send!"
            )
            return
        channel = int(channel)
        chan = self.bot.get_channel(channel)
        if chan is None:
            await ctx.respond(f"{Emojis.failure} Channel not found.")
            return

        try:
            data = json.loads(embed)
        except json.JSONDecodeError:
            await ctx.respond(f"{Emojis.failure} Invalid JSON.")
            return

        content = ""
        if "content" in data:
            content = data["content"]

        embeds = []
        if "embeds" in data:
            for embed in data["embeds"]:
                emb = discord.Embed(
                    title=embed["title"],
                    description=embed["description"],
                    color=discord.Color(embed["color"]),
                )
                for field in embed["fields"]:
                    emb.add_field(
                        name=field["name"], value=field["value"], inline=field["inline"]
                    )
                embeds.append(emb)

        await chan.send(content, embeds=embeds)
        await ctx.respond(f"{Emojis.success} Message sent!")


def setup(bot):
    bot.add_cog(Owner(bot))
