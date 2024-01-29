from asyncio import sleep
import discord
import random
from discord.ext import commands


class Games(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(description="Flip a coin!")
    async def coinflip(self, ctx: discord.ApplicationContext):
        """
        Flips a coin
        """
        await ctx.respond("Look below! v")
        current_flip = "heads"
        msg = await ctx.send(f"Flipping...  [{current_flip}]")
        num_flips = random.randint(10, 20)
        for idx in range(num_flips):
            current_flip = "heads" if current_flip == "tails" else "tails"
            await msg.edit(content=f"Flipping...  [{current_flip}]")
            await sleep(2 * (idx / num_flips))
        current_flip = "heads" if current_flip == "tails" else "tails"
        await msg.edit(content=f"Its {current_flip}!")

    @commands.slash_command(description="Roll a dice")
    async def dice(self, ctx: discord.ApplicationContext, sides: int = 6, num_dice: int = 1):
        """
        Flips a coin
        """
        await ctx.respond("Look below! v")
        current_rolls = [str(random.randint(1, sides)) for _ in range(num_dice)]
        msg = await ctx.send(f"Rolling... {', '.join(current_rolls)}")
        num_rolls = random.randint(3, 6)
        for idx in range(num_rolls):
            current_rolls = [str(random.randint(1, sides)) for _ in range(num_dice)]
            await msg.edit(content=f"Rolling... {', '.join(current_rolls)}")
            await sleep(0.5 * (idx / num_rolls))
        current_rolls = [int(random.randint(1, sides)) for _ in range(num_dice)]
        await msg.edit(content=f"Your rolls: {', '.join([str(s) for s in current_rolls])}!\nMinimum: {min(current_rolls)}\nAverage: {sum(current_rolls)/len(current_rolls)}\nMaximum: {max(current_rolls)}")

def setup(bot):
    bot.add_cog(Games(bot))
