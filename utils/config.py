import discord
import json
import os
import time
from typing import Dict
from collections import OrderedDict


class Config:
    bot: discord.Bot

    _version: str = ""
    last_version_update: float = 0.0

    _changelog: Dict[str, Dict[str, str]] = {}
    last_changelog_update: float = 0.0

    @property
    def version(self) -> str:
        if time.time() - self.last_version_update > 5 * 60:
            with open(os.path.join("config", "version.txt")) as f:
                self.__class___.version = f.readline().replace("\n", "")
            self.last_version_update = time.time()

        return self._version

    @classmethod
    def changelog(cls) -> Dict[str, Dict[str, str]]:
        if time.time() - cls.last_changelog_update > 5 * 60:
            with open(os.path.join("config", "changelog.json")) as f:
                cls._changelog = json.load(f)
            cls._changelog = OrderedDict(sorted(cls._changelog.items()))
            cls.last_changelog_update = time.time()

        return cls._changelog
