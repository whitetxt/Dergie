import tarfile
import threading
import discord
import requests
import re
from typing import List
from discord.ext import commands, tasks
from utils.settings import *
from utils.helpers import *


class AutoMod(commands.Cog):
    bot: discord.Bot

    bad_url_overrides: List[str] = []
    bad_urls: List[str] = []

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        bot.tasks.append(self.update_bad_urls)
        if os.path.exists("databases/cached-urls.txt"):
            with open("databases/cached-urls.txt", "r") as f:
                self.bad_urls = [line.strip() for line in f.readlines()]

    @tasks.loop(hours=1)
    async def update_bad_urls(self):
        thread = threading.Thread(target=self.update_bad_urls_thread)
        thread.start()

    def update_bad_urls_thread(self):
        print("Downloading URL .tar.gz")
        url = "https://raw.githubusercontent.com/mitchellkrogza/Phishing.Database/master/ALL-phishing-domains.tar.gz"
        response = requests.get(url)
        if response.status_code == 200:
            with open("urls.tar.gz", "wb") as f:
                f.write(response.content)

        print("Downloaded URL .tar.gz")

        with tarfile.open("urls.tar.gz", "r:gz") as tar:
            for member in tar.getmembers():
                if "phishing" in member.name:
                    f = tar.extractfile(member)
                    if f is not None:
                        self.bad_urls = [
                            line.strip().decode() for line in f.readlines()
                        ]
                        with open("databases/cached-urls.txt", "w") as f:
                            f.writelines([url + "\n" for url in self.bad_urls])

        os.remove("urls.tar.gz")

        print(f"Loaded & cached phishing {len(self.bad_urls)} URLs")

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if not message.guild:
            return
        guild = message.guild

        settings = Settings.get_settings(guild.id)
        if settings is None:
            return

        if settings.automod_enabled:
            await self.check_automod_trigger(message)

    async def check_automod_trigger(self, message: discord.Message):
        # Check for any dangerous URLs
        urls = self.check_bad_urls(message)
        if urls is not None:
            await message.delete()
            urls = [url for url in urls if url not in self.bad_url_overrides]
            if len(", ".join(urls)) > 1000:
                urlsToSend = urls[0]
                urls = urls[1:]
                while len(urlsToSend) < 1000 and len(urls) > 0:
                    urlsToSend += ", " + urls[0]
                    urls = urls[1:]
                urlsToSend = ", ".join(urlsToSend.split(", ")[:-1]) + " & more"
            else:
                urlsToSend = ", ".join(urls)
            await message.author.send(
                f"""{Emojis.failure} Warning! {Emojis.failure}
Your recent message in `{message.guild.name}` has been deleted as it was determined to have dangerous URLs in it.
Please review what you are sending and try again!
Detected dangerous URLs: {urlsToSend}

If you think this is a false positive, please open a ticket in the support server: {Details.support_url}"""
            )
        return

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.on_message(after)

    def check_bad_urls(self, message: discord.Message):
        # TODO:
        # Rewrite this.
        urls = re.findall(
            "(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}$)",
            message.content,
        )
        if len(urls) == 0:
            return None
        bad_urls = []
        for url in urls:
            if url in self.bad_urls:
                bad_urls.append(url)
        return bad_urls


def setup(bot):
    bot.add_cog(AutoMod(bot))
