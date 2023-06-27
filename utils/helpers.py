import discord


class Emojis:
    success: str = "<:success:1054875537367113739>"
    failure: str = "<:failure:1054875536679243877>"
    warning: str = "<:warn:1086725292908883998>"


class Details:
    support_url: str = "https://discord.gg/8B5BfM8Szp"
    owner: str = "_whitetxt#6483"
    contact_email: str = "N/A"


def format_username(user: discord.User):
    return f"{user.name}{f'#{user.discriminator}' if user.discriminator != '0' else ''}"
