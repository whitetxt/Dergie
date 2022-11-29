import discord
import json
import os
import time
from typing import Dict
from collections import OrderedDict

class Config:
	bot: discord.AutoShardedBot

	_version: str = ""
	last_version_update: float = 0.0

	_changelog: Dict[str, Dict[str, str]] = {}
	last_changelog_update: float = 0.0

	def __init__(self, bot: discord.AutoShardedBot):
		self.bot = bot
		with open(os.path.join("config", "version.txt")) as f:
			self.__class__._version = f.readline().replace("\n", "")
		self.last_version_update = time.time()

		with open(os.path.join("config", "changelog.json")) as f:
			self.__class__._changelog = json.load(f)
		self.__class__._changelog = OrderedDict(sorted(self._changelog.items()))
		self.last_changelog_update = time.time()

	@property
	def version(self) -> str:
		if time.time() - self.last_version_update > 5 * 60:
			with open(os.path.join("config", "version.txt")) as f:
				self.__class___.version = f.readline().replace("\n", "")
			self.last_version_update = time.time()

		return self._version

	@property
	def changelog(self) -> Dict[str, Dict[str, str]]:
		if time.time() - self.last_changelog_update > 5 * 60:
			with open(os.path.join("config", "changelog.json")) as f:
				self.__class__._changelog = json.load(f)
			self.__class__._changelog = OrderedDict(sorted(self._changelog.items()))
			self.last_changelog_update = time.time()

		return self._changelog